"""Use case that marks an ad as sold or reactivates it (spec 011)."""

from datetime import timedelta

import pytest

from server.core.usecases.alterar_status_anuncio import AlterarStatusAnuncio
from server.core.usecases.erros import (
    AnuncioDeOutroUsuario,
    AnuncioNaoEncontrado,
    MudancaDeStatusInvalida,
    StatusInvalido,
)
from tests.core.usecases.test_gerenciar_anuncio import (
    AGORA,
    DONO,
    OUTRA_PESSOA,
    AnuncioEditavelRepositoryEmMemoria,
    RelogioFixo,
    anuncio_salvo,
)


def alterar(anuncio, novo_status, usuario_id=DONO):
    repositorio = AnuncioEditavelRepositoryEmMemoria([anuncio])
    caso_de_uso = AlterarStatusAnuncio(repositorio, RelogioFixo())
    return caso_de_uso.executar(1, usuario_id, novo_status), repositorio


@pytest.mark.parametrize("status_atual", ["published", "expired"])
def test_dono_marca_publicado_ou_expirado_como_vendido(status_atual):
    vendido, repositorio = alterar(
        anuncio_salvo(status=status_atual), "sold"
    )

    assert vendido.status == "sold"
    assert repositorio.buscar_por_id(1).status == "sold"


def test_marcar_vendido_de_novo_nao_e_erro():
    vendido, _ = alterar(anuncio_salvo(status="sold"), "sold")

    assert vendido.status == "sold"


@pytest.mark.parametrize("categoria", ["produto", "servico", "evento"])
def test_vale_para_qualquer_categoria(categoria):
    vendido, _ = alterar(
        anuncio_salvo(category=categoria, estado_conservacao=None), "sold"
    )

    assert vendido.status == "sold"


def test_reativar_dentro_do_prazo_volta_a_publicado():
    anuncio = anuncio_salvo(
        status="sold", expires_at=AGORA + timedelta(days=5)
    )

    reativado, _ = alterar(anuncio, "published")

    assert reativado.status == "published"
    assert reativado.expires_at == AGORA + timedelta(days=5)


def test_reativar_fora_do_prazo_volta_como_expirado():
    anuncio = anuncio_salvo(
        status="sold", expires_at=AGORA - timedelta(seconds=1)
    )

    reativado, _ = alterar(anuncio, "published")

    assert reativado.status == "expired"


@pytest.mark.parametrize("status_atual", ["published", "expired"])
def test_reativar_recusa_anuncio_que_nao_esta_vendido(status_atual):
    anuncio = anuncio_salvo(status=status_atual)

    with pytest.raises(MudancaDeStatusInvalida):
        alterar(anuncio, "published")


@pytest.mark.parametrize("novo_status", ["expired", "deleted", "", None])
def test_recusa_status_desconhecido(novo_status):
    with pytest.raises(StatusInvalido):
        alterar(anuncio_salvo(), novo_status)


@pytest.mark.parametrize("dono_do_anuncio", [OUTRA_PESSOA, None])
def test_recusa_quem_nao_e_dono(dono_do_anuncio):
    anuncio = anuncio_salvo(usuario_id=dono_do_anuncio)
    repositorio = AnuncioEditavelRepositoryEmMemoria([anuncio])

    with pytest.raises(AnuncioDeOutroUsuario):
        AlterarStatusAnuncio(repositorio, RelogioFixo()).executar(
            1, DONO, "sold"
        )

    assert repositorio.buscar_por_id(1).status == "published"


def test_recusa_anuncio_inexistente():
    repositorio = AnuncioEditavelRepositoryEmMemoria([])

    with pytest.raises(AnuncioNaoEncontrado):
        AlterarStatusAnuncio(repositorio, RelogioFixo()).executar(
            99, DONO, "sold"
        )
