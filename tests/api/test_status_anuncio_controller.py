"""PATCH /api/ads/<id>/status and the sold listing (spec 011, PROJ-35)."""

import pytest

from server.infra.db.models import AdModel
from tests.api.test_ads_controller import (
    complete_advertiser_profile,
    create_ads_app,
)
from tests.api.test_gerenciar_anuncio_controller import (
    entrar_como_outra_pessoa,
    publicar,
)


@pytest.fixture
def app():
    aplicacao = create_ads_app()
    complete_advertiser_profile(aplicacao)
    yield aplicacao
    aplicacao.extensions["database_engine"].dispose()


def headers(app):
    return app.extensions["test_auth_headers"]


def mudar_status(app, ad_id, corpo, cabecalhos=None):
    return app.test_client().patch(
        f"/api/ads/{ad_id}/status",
        json=corpo,
        headers=cabecalhos if cabecalhos is not None else headers(app),
    )


def titulos(app, consulta=""):
    resposta = app.test_client().get(
        f"/api/ads{consulta}", headers=headers(app)
    )
    assert resposta.status_code == 200, resposta.json
    return [item["title"] for item in resposta.json["items"]]


def test_dono_marca_como_vendido_e_o_anuncio_sai_do_feed(app):
    ad_id = publicar(app)
    assert "Livro de Cálculo" in titulos(app)

    resposta = mudar_status(app, ad_id, {"status": "sold"})

    assert resposta.status_code == 200
    assert resposta.json["id"] == ad_id
    assert resposta.json["status"] == "sold"
    assert resposta.json["expires_at"]
    assert "Livro de Cálculo" not in titulos(app)
    assert "Livro de Cálculo" not in titulos(app, "?search=livro")


def test_dono_lista_seus_vendidos_no_painel(app):
    ad_id = publicar(app)
    mudar_status(app, ad_id, {"status": "sold"})

    assert titulos(app, "?owner=me&status=sold") == ["Livro de Cálculo"]
    assert "Livro de Cálculo" not in titulos(
        app, "?owner=me&status=published"
    )


def test_vendidos_so_podem_ser_listados_pelo_dono(app):
    resposta = app.test_client().get(
        "/api/ads?status=sold", headers=headers(app)
    )

    assert resposta.status_code == 400
    assert "owner=me" in resposta.json["message"]


def test_dono_reativa_e_o_anuncio_volta_ao_feed(app):
    ad_id = publicar(app)
    mudar_status(app, ad_id, {"status": "sold"})

    resposta = mudar_status(app, ad_id, {"status": "published"})

    assert resposta.status_code == 200
    assert resposta.json["status"] == "published"
    assert "Livro de Cálculo" in titulos(app)


def test_reativar_anuncio_publicado_responde_422(app):
    ad_id = publicar(app)

    resposta = mudar_status(app, ad_id, {"status": "published"})

    assert resposta.status_code == 422
    assert resposta.json["code"] == "mudanca_de_status_invalida"


@pytest.mark.parametrize(
    "corpo",
    [{"status": "expired"}, {"status": "vendido"}, {"status": 1}, {}],
)
def test_status_desconhecido_responde_422(app, corpo):
    ad_id = publicar(app)

    resposta = mudar_status(app, ad_id, corpo)

    assert resposta.status_code == 422
    assert resposta.json["code"] == "status_invalido"


def test_corpo_que_nao_e_json_responde_415(app):
    ad_id = publicar(app)

    resposta = app.test_client().patch(
        f"/api/ads/{ad_id}/status",
        data={"status": "sold"},
        headers=headers(app),
    )

    assert resposta.status_code == 415


def test_outra_pessoa_nao_muda_o_status(app):
    ad_id = publicar(app)
    headers_bruno = entrar_como_outra_pessoa(app)

    resposta = mudar_status(app, ad_id, {"status": "sold"}, headers_bruno)

    assert resposta.status_code == 403
    with app.extensions["session_factory"]() as session:
        assert session.get(AdModel, ad_id).status == "published"


def test_anuncio_inexistente_responde_404(app):
    resposta = mudar_status(app, 9999, {"status": "sold"})

    assert resposta.status_code == 404


def test_mudar_status_exige_login(app):
    ad_id = publicar(app)

    resposta = app.test_client().patch(
        f"/api/ads/{ad_id}/status", json={"status": "sold"}
    )

    assert resposta.status_code == 401
