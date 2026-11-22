"""PUT and DELETE /api/ads/<id> (spec 007, PROJ-38)."""

from datetime import datetime, timedelta, timezone
from io import BytesIO

import pytest
from werkzeug.security import generate_password_hash

from server.infra.db.models import AdModel, UsuarioModel
from tests.api.test_ads_controller import (
    complete_advertiser_profile,
    create_ads_app,
)

LIVRO = {
    "titulo": "Livro de Cálculo",
    "categoria": "produto",
    "estado_conservacao": "novo",
    "descricao": "Livro em bom estado.",
    "preco": 40,
}


def publicar(app, dados=LIVRO):
    resposta = app.test_client().post(
        "/api/ads", json=dados, headers=app.extensions["test_auth_headers"]
    )
    assert resposta.status_code == 201
    return resposta.json["id"]


def entrar_como_outra_pessoa(app):
    with app.extensions["session_factory"].begin() as session:
        session.add(
            UsuarioModel(
                nome="Bruno",
                email="bruno@aluno.puc-rio.br",
                nome_usuario="bruno",
                vinculo="aluno",
                senha_hash=generate_password_hash("Senha123"),
                confirmado_em=datetime.now(timezone.utc),
            )
        )
    login = app.test_client().post(
        "/auth/login",
        json={"identificador": "bruno", "senha": "Senha123"},
    )
    assert login.status_code == 200
    return {"Authorization": f"Bearer {login.json['token']}"}


def precos_no_feed(app):
    feed = app.test_client().get(
        "/api/ads", headers=app.extensions["test_auth_headers"]
    )
    return {item["title"]: item["price"] for item in feed.json["items"]}


@pytest.fixture
def app():
    aplicacao = create_ads_app()
    complete_advertiser_profile(aplicacao)
    yield aplicacao
    aplicacao.extensions["database_engine"].dispose()


def test_dono_edita_preco_e_o_feed_mostra_o_novo_valor(app):
    ad_id = publicar(app)

    resposta = app.test_client().put(
        f"/api/ads/{ad_id}",
        json={**LIVRO, "titulo": "Livro de Cálculo 1", "preco": "35,50"},
        headers=app.extensions["test_auth_headers"],
    )

    assert resposta.status_code == 200
    assert resposta.json["id"] == ad_id
    assert resposta.json["title"] == "Livro de Cálculo 1"
    assert resposta.json["price"] == 35.5
    assert resposta.json["nome_anunciante"] == "Ana Vendas"
    assert "usuario_id" not in resposta.json
    assert precos_no_feed(app)["Livro de Cálculo 1"] == 35.5


def test_editar_anuncio_expirado_renova_apos_salvar(app):
    ad_id = publicar(app)
    agora = datetime.now(timezone.utc)
    with app.extensions["session_factory"].begin() as session:
        anuncio_expirado = session.get(AdModel, ad_id)
        anuncio_expirado.status = "expired"
        anuncio_expirado.expires_at = agora - timedelta(days=1)

    resposta = app.test_client().put(
        f"/api/ads/{ad_id}",
        json={**LIVRO, "titulo": "Livro revisado"},
        headers=app.extensions["test_auth_headers"],
    )

    assert resposta.status_code == 200
    with app.extensions["session_factory"]() as session:
        anuncio_salvo = session.get(AdModel, ad_id)
        assert anuncio_salvo.status == "published"
        assert anuncio_salvo.expires_at > agora + timedelta(days=29)
        assert anuncio_salvo.expires_at < agora + timedelta(days=31)


def test_dono_troca_para_a_combinar(app):
    ad_id = publicar(app)
    dados = {**LIVRO, "preco_a_combinar": True}
    dados.pop("preco")

    resposta = app.test_client().put(
        f"/api/ads/{ad_id}",
        json=dados,
        headers=app.extensions["test_auth_headers"],
    )

    assert resposta.status_code == 200
    assert resposta.json["preco_a_combinar"] is True
    assert resposta.json["price"] is None


def test_edicao_invalida_mostra_erros_por_campo_e_nao_muda_nada(app):
    ad_id = publicar(app)

    resposta = app.test_client().put(
        f"/api/ads/{ad_id}",
        json={**LIVRO, "titulo": "abc", "preco": -1, "usuario_id": 2},
        headers=app.extensions["test_auth_headers"],
    )

    assert resposta.status_code == 422
    assert set(resposta.json["campos"]) == {"titulo", "preco", "usuario_id"}
    assert precos_no_feed(app)["Livro de Cálculo"] == 40


def test_edicao_recusa_troca_de_categoria(app):
    ad_id = publicar(app)
    dados = {**LIVRO, "categoria": "servico"}
    dados.pop("estado_conservacao")

    resposta = app.test_client().put(
        f"/api/ads/{ad_id}",
        json=dados,
        headers=app.extensions["test_auth_headers"],
    )

    assert resposta.status_code == 422
    assert resposta.json["campos"] == {
        "categoria": "A categoria do anúncio não pode ser alterada."
    }


def test_edicao_aceita_so_json(app):
    ad_id = publicar(app)

    resposta = app.test_client().put(
        f"/api/ads/{ad_id}",
        data={"titulo": "Livro de Cálculo 1"},
        headers=app.extensions["test_auth_headers"],
    )

    assert resposta.status_code == 415
    assert resposta.is_json


def test_outra_pessoa_nao_edita_nem_exclui(app):
    ad_id = publicar(app)
    headers_bruno = entrar_como_outra_pessoa(app)
    cliente = app.test_client()

    edicao = cliente.put(
        f"/api/ads/{ad_id}",
        json={**LIVRO, "preco": 1},
        headers=headers_bruno,
    )
    exclusao = cliente.delete(f"/api/ads/{ad_id}", headers=headers_bruno)

    assert edicao.status_code == 403
    assert edicao.json["code"] == "anuncio_de_outro_usuario"
    assert exclusao.status_code == 403
    assert precos_no_feed(app)["Livro de Cálculo"] == 40


def test_anuncio_sem_dono_nao_pode_ser_editado(app):
    with app.extensions["session_factory"]() as session:
        antigo = session.query(AdModel).filter_by(
            title="Bicicleta urbana"
        ).one()

    resposta = app.test_client().delete(
        f"/api/ads/{antigo.id}",
        headers=app.extensions["test_auth_headers"],
    )

    assert resposta.status_code == 403


@pytest.mark.parametrize("metodo", ["put", "delete"])
def test_anuncio_inexistente_responde_404(app, metodo):
    resposta = getattr(app.test_client(), metodo)(
        "/api/ads/9999",
        json=LIVRO,
        headers=app.extensions["test_auth_headers"],
    )

    assert resposta.status_code == 404
    assert resposta.json["code"] == "anuncio_nao_encontrado"


@pytest.mark.parametrize("metodo", ["put", "delete"])
def test_gerenciar_exige_login(app, metodo):
    ad_id = publicar(app)

    resposta = getattr(app.test_client(), metodo)(
        f"/api/ads/{ad_id}", json=LIVRO
    )

    assert resposta.status_code == 401


def test_dono_exclui_e_o_anuncio_some_do_banco_e_do_feed(app):
    ad_id = publicar(app)

    resposta = app.test_client().delete(
        f"/api/ads/{ad_id}", headers=app.extensions["test_auth_headers"]
    )

    assert resposta.status_code == 204
    assert resposta.data == b""
    assert "Livro de Cálculo" not in precos_no_feed(app)
    with app.extensions["session_factory"]() as session:
        assert session.get(AdModel, ad_id) is None


def test_excluir_apaga_a_foto_do_armazenamento(tmp_path):
    app = create_ads_app(tmp_path / "media")
    complete_advertiser_profile(app)
    headers = app.extensions["test_auth_headers"]
    cliente = app.test_client()
    publicado = cliente.post(
        "/api/ads",
        data={
            "titulo": "Cartaz do evento",
            "categoria": "evento",
            "descricao": "Evento aberto à comunidade.",
            "preco": "0",
            "imagem": (BytesIO(b"\x89PNG\r\n\x1a\nconteudo"), "cartaz.png"),
        },
        headers=headers,
    )
    assert publicado.status_code == 201
    image_url = publicado.json["image_url"]
    assert cliente.get(image_url).status_code == 200

    resposta = cliente.delete(
        f"/api/ads/{publicado.json['id']}", headers=headers
    )

    assert resposta.status_code == 204
    assert cliente.get(image_url).status_code == 404
    assert not any(path.is_file() for path in (tmp_path / "media").rglob("*"))
    app.extensions["database_engine"].dispose()
