from dataclasses import replace
from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest

from server.core.entities.ad import Ad
from server.core.entities.anuncio import Anuncio
from server.core.interfaces.anuncio_editavel_repository_interface import (
    AnuncioEditavelRepositoryInterface,
)
from server.core.usecases.editar_anuncio import EditarAnuncio
from server.core.usecases.erros import (
    AnuncioDeOutroUsuario,
    AnuncioNaoEncontrado,
    CategoriaNaoEditavel,
)
from server.core.usecases.excluir_anuncio import ExcluirAnuncio
from server.core.usecases.renovar_anuncio import RenovarAnuncio
from server.core.usecases.erros import AnuncioNaoExpirado

DONO = 7
OUTRA_PESSOA = 8
CRIADO_EM = datetime(2026, 11, 20, 12, 0, tzinfo=UTC)
EXPIRA_EM = CRIADO_EM + timedelta(days=30)
AGORA = datetime(2026, 11, 22, 12, 0, tzinfo=UTC)


class RelogioFixo:
    def agora(self):
        return AGORA


class AnuncioEditavelRepositoryEmMemoria(AnuncioEditavelRepositoryInterface):
    def __init__(self, anuncios):
        self.anuncios = {ad.id: ad for ad in anuncios}
        self.excluidos = []

    def buscar_por_id(self, ad_id):
        return self.anuncios.get(ad_id)

    def atualizar(self, ad_id, anuncio, expires_at=None):
        atual = self.anuncios[ad_id]
        self.anuncios[ad_id] = replace(
            atual,
            title=anuncio.titulo,
            description=anuncio.descricao,
            price=None if anuncio.preco is None else float(anuncio.preco),
            preco_a_combinar=anuncio.preco is None,
            estado_conservacao=anuncio.estado_conservacao,
            status="published" if expires_at is not None else atual.status,
            expires_at=(
                expires_at if expires_at is not None else atual.expires_at
            ),
        )
        return self.anuncios[ad_id]

    def excluir(self, ad_id):
        self.excluidos.append(ad_id)
        del self.anuncios[ad_id]

    def renovar(self, ad_id, expires_at):
        atual = self.anuncios[ad_id]
        self.anuncios[ad_id] = replace(
            atual,
            status="published",
            expires_at=expires_at,
        )
        return self.anuncios[ad_id]


def anuncio_salvo(ad_id=1, usuario_id=DONO, category="produto", **extras):
    dados = {
        "id": ad_id,
        "title": "Livro de Cálculo",
        "description": "Livro em bom estado.",
        "type": "product" if category == "produto" else "service",
        "category": category,
        "price": 40.0,
        "created_at": CRIADO_EM,
        "status": "published",
        "expires_at": EXPIRA_EM,
        "usuario_id": usuario_id,
        "estado_conservacao": "novo" if category == "produto" else None,
        "image_key": "anuncios/livro.webp",
    }
    dados.update(extras)
    return Ad(**dados)


def edicao(usuario_id=DONO, categoria="produto", **extras):
    dados = {
        "usuario_id": usuario_id,
        "titulo": "Livro de Cálculo 1",
        "descricao": "Livro com poucas anotações.",
        "categoria": categoria,
        "preco": Decimal("35.50"),
        "estado_conservacao": (
            "usado_regular" if categoria == "produto" else None
        ),
    }
    dados.update(extras)
    return Anuncio(**dados)


def test_dono_edita_campos_e_mantem_datas_situacao_e_foto():
    repositorio = AnuncioEditavelRepositoryEmMemoria([anuncio_salvo()])

    editado = EditarAnuncio(repositorio, RelogioFixo()).executar(
        1, edicao()
    )

    assert editado.title == "Livro de Cálculo 1"
    assert editado.description == "Livro com poucas anotações."
    assert editado.price == 35.5
    assert editado.estado_conservacao == "usado_regular"
    assert editado.created_at == CRIADO_EM
    assert editado.expires_at == EXPIRA_EM
    assert editado.status == "published"
    assert editado.image_key == "anuncios/livro.webp"


def test_dono_troca_preco_para_a_combinar():
    repositorio = AnuncioEditavelRepositoryEmMemoria(
        [anuncio_salvo(category="servico")]
    )

    editado = EditarAnuncio(repositorio, RelogioFixo()).executar(
        1, edicao(categoria="servico", preco=None)
    )

    assert editado.preco_a_combinar is True
    assert editado.price is None


def test_editar_anuncio_expirado_publica_e_define_novo_prazo():
    repositorio = AnuncioEditavelRepositoryEmMemoria(
        [anuncio_salvo(status="expired")]
    )

    editado = EditarAnuncio(repositorio, RelogioFixo()).executar(
        1, edicao()
    )

    assert editado.status == "published"
    assert editado.title == "Livro de Cálculo 1"
    assert editado.created_at == CRIADO_EM
    assert editado.expires_at == AGORA + timedelta(days=30)


def test_editar_recusa_troca_de_categoria():
    original = anuncio_salvo()
    repositorio = AnuncioEditavelRepositoryEmMemoria([original])

    with pytest.raises(CategoriaNaoEditavel):
        EditarAnuncio(repositorio, RelogioFixo()).executar(
            1, edicao(categoria="servico")
        )

    assert repositorio.buscar_por_id(1) == original


@pytest.mark.parametrize("usuario_id_do_anuncio", [OUTRA_PESSOA, None])
def test_editar_recusa_quem_nao_e_dono(usuario_id_do_anuncio):
    original = anuncio_salvo(usuario_id=usuario_id_do_anuncio)
    repositorio = AnuncioEditavelRepositoryEmMemoria([original])

    with pytest.raises(AnuncioDeOutroUsuario):
        EditarAnuncio(repositorio, RelogioFixo()).executar(1, edicao())

    assert repositorio.buscar_por_id(1) == original


def test_editar_anuncio_inexistente():
    repositorio = AnuncioEditavelRepositoryEmMemoria([])

    with pytest.raises(AnuncioNaoEncontrado):
        EditarAnuncio(repositorio, RelogioFixo()).executar(99, edicao())


def test_dono_exclui_e_recebe_a_chave_da_foto():
    repositorio = AnuncioEditavelRepositoryEmMemoria([anuncio_salvo()])

    chave = ExcluirAnuncio(repositorio).executar(1, DONO)

    assert chave == "anuncios/livro.webp"
    assert repositorio.excluidos == [1]
    assert repositorio.buscar_por_id(1) is None


def test_excluir_anuncio_sem_foto_devolve_none():
    repositorio = AnuncioEditavelRepositoryEmMemoria(
        [anuncio_salvo(image_key=None)]
    )

    assert ExcluirAnuncio(repositorio).executar(1, DONO) is None
    assert repositorio.excluidos == [1]


@pytest.mark.parametrize("usuario_id_do_anuncio", [OUTRA_PESSOA, None])
def test_excluir_recusa_quem_nao_e_dono(usuario_id_do_anuncio):
    repositorio = AnuncioEditavelRepositoryEmMemoria(
        [anuncio_salvo(usuario_id=usuario_id_do_anuncio)]
    )

    with pytest.raises(AnuncioDeOutroUsuario):
        ExcluirAnuncio(repositorio).executar(1, DONO)

    assert repositorio.excluidos == []


def test_excluir_anuncio_inexistente():
    repositorio = AnuncioEditavelRepositoryEmMemoria([])

    with pytest.raises(AnuncioNaoEncontrado):
        ExcluirAnuncio(repositorio).executar(99, DONO)


def test_dono_renova_anuncio_expirado_por_30_dias():
    original = anuncio_salvo(status="expired")
    repositorio = AnuncioEditavelRepositoryEmMemoria([original])

    class Relogio:
        def agora(self):
            return CRIADO_EM

    renovado = RenovarAnuncio(repositorio, Relogio()).executar(1, DONO)

    assert renovado.status == "published"
    assert renovado.expires_at == CRIADO_EM + timedelta(days=30)


def test_renovacao_recusa_anuncio_publicado():
    repositorio = AnuncioEditavelRepositoryEmMemoria(
        [anuncio_salvo(status="published")]
    )

    class Relogio:
        def agora(self):
            return CRIADO_EM

    with pytest.raises(AnuncioNaoExpirado):
        RenovarAnuncio(repositorio, Relogio()).executar(1, DONO)


@pytest.mark.parametrize("usuario_id_do_anuncio", [OUTRA_PESSOA, None])
def test_renovacao_recusa_quem_nao_e_dono(usuario_id_do_anuncio):
    repositorio = AnuncioEditavelRepositoryEmMemoria(
        [anuncio_salvo(status="expired", usuario_id=usuario_id_do_anuncio)]
    )

    class Relogio:
        def agora(self):
            return CRIADO_EM

    with pytest.raises(AnuncioDeOutroUsuario):
        RenovarAnuncio(repositorio, Relogio()).executar(1, DONO)
