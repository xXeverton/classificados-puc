"""Find, update and delete operations of the advertisement repository."""

from datetime import UTC, datetime, timedelta
from decimal import Decimal

from server.core.entities.anuncio import Anuncio
from server.infra.db.database import create_session_factory
from server.infra.db.models import AdModel, UsuarioModel
from server.infra.gateways.ad_repository_sqlalchemy import (
    AdRepositorySQLAlchemy,
)

CRIADO_EM = datetime(2026, 11, 20, 12, 0, tzinfo=UTC)
EXPIRA_EM = CRIADO_EM + timedelta(days=30)


def preparar(database_engine):
    session_factory = create_session_factory(database_engine)
    with session_factory.begin() as session:
        session.add(
            UsuarioModel(
                nome="Ana",
                email="ana@aluno.puc-rio.br",
                nome_usuario="ana123",
                vinculo="aluno",
                senha_hash="hash",
                confirmado_em=CRIADO_EM,
            )
        )
    return AdRepositorySQLAlchemy(session_factory), session_factory


def anuncio(**extras):
    dados = {
        "usuario_id": 1,
        "titulo": "Livro de Cálculo",
        "descricao": "Livro em bom estado.",
        "categoria": "produto",
        "preco": Decimal("40"),
        "estado_conservacao": "novo",
        "image_key": "anuncios/livro.webp",
    }
    dados.update(extras)
    return Anuncio(**dados)


def publicar(repositorio, **extras):
    return repositorio.publish(anuncio(**extras), "Ana", CRIADO_EM, EXPIRA_EM)


def test_busca_anuncio_com_dono_e_chave_da_foto(database_engine):
    repositorio, _ = preparar(database_engine)
    publicado = publicar(repositorio)

    encontrado = repositorio.buscar_por_id(publicado.id)

    assert encontrado.title == "Livro de Cálculo"
    assert encontrado.usuario_id == 1
    assert encontrado.image_key == "anuncios/livro.webp"
    assert encontrado.category == "produto"


def test_busca_inclui_anuncio_expirado_e_devolve_none_se_nao_existe(
    database_engine,
):
    repositorio, session_factory = preparar(database_engine)
    publicado = publicar(repositorio)
    with session_factory.begin() as session:
        session.get(AdModel, publicado.id).status = "expired"

    assert repositorio.buscar_por_id(publicado.id).status == "expired"
    assert repositorio.buscar_por_id(999) is None


def test_atualiza_campos_editaveis_e_mantem_o_resto(database_engine):
    repositorio, session_factory = preparar(database_engine)
    publicado = publicar(repositorio)

    editado = repositorio.atualizar(
        publicado.id,
        anuncio(
            titulo="Livro de Cálculo 1",
            descricao="Com poucas anotações.",
            preco=Decimal("35.50"),
            estado_conservacao="usado_regular",
            image_key=None,
        ),
    )

    assert editado.title == "Livro de Cálculo 1"
    assert editado.description == "Com poucas anotações."
    assert editado.price == 35.5
    assert editado.estado_conservacao == "usado_regular"
    # No advertiser profile in this test, so there is no display name.
    assert editado.nome_anunciante is None
    with session_factory() as session:
        model = session.get(AdModel, publicado.id)
        assert model.created_at == CRIADO_EM
        assert model.expires_at == EXPIRA_EM
        assert model.status == "published"
        assert model.usuario_id == 1
        assert model.image_key == "anuncios/livro.webp"


def test_atualiza_para_preco_a_combinar(database_engine):
    repositorio, session_factory = preparar(database_engine)
    publicado = publicar(
        repositorio, categoria="servico", estado_conservacao=None
    )

    editado = repositorio.atualizar(
        publicado.id,
        anuncio(categoria="servico", estado_conservacao=None, preco=None),
    )

    assert editado.preco_a_combinar is True
    assert editado.price is None
    with session_factory() as session:
        model = session.get(AdModel, publicado.id)
        assert model.preco_a_combinar is True
        assert model.price == 0


def test_atualiza_anuncio_expirado_e_publica_com_novo_prazo(database_engine):
    repositorio, session_factory = preparar(database_engine)
    publicado = publicar(repositorio)
    novo_prazo = CRIADO_EM + timedelta(days=45)
    with session_factory.begin() as session:
        session.get(AdModel, publicado.id).status = "expired"

    editado = repositorio.atualizar(
        publicado.id,
        anuncio(titulo="Livro de Cálculo revisado"),
        expires_at=novo_prazo,
    )

    assert editado.status == "published"
    assert editado.expires_at == novo_prazo
    with session_factory() as session:
        model = session.get(AdModel, publicado.id)
        assert model.status == "published"
        assert model.expires_at == novo_prazo


def test_exclui_anuncio_do_banco(database_engine):
    repositorio, session_factory = preparar(database_engine)
    publicado = publicar(repositorio)
    outro = publicar(repositorio, titulo="Outro anúncio")

    repositorio.excluir(publicado.id)

    assert repositorio.buscar_por_id(publicado.id) is None
    assert repositorio.buscar_por_id(outro.id) is not None
    with session_factory() as session:
        assert session.get(AdModel, publicado.id) is None


def test_altera_so_o_status_e_mantem_o_resto(database_engine):
    repositorio, session_factory = preparar(database_engine)
    publicado = publicar(repositorio)

    vendido = repositorio.alterar_status(publicado.id, "sold")

    assert vendido.status == "sold"
    assert vendido.title == publicado.title
    with session_factory() as session:
        model = session.get(AdModel, publicado.id)
        assert model.status == "sold"
        assert model.expires_at == EXPIRA_EM
        assert model.image_key == "anuncios/livro.webp"
