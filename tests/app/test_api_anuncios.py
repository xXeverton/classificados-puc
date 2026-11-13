import json

import pytest
from flask import abort

from app.database import get_db
from app.main import create_app
from infra.repositories.memoria import UsuarioRepositoryMemoria
from infra.seguranca.verificador_senha_werkzeug import (
    VerificadorSenhaWerkzeug,
)
from tests.fakes import criar_usuario

_EMAIL = "ana@aluno.puc-rio.br"
_SENHA = "senha-correta"
_SEGREDO_JWT = "segredo-de-teste-com-tamanho-suficiente"


def _falha_api():
    raise RuntimeError("detalhe interno não deve ser exposto")


@pytest.fixture
def api_client(tmp_path):
    usuario = criar_usuario(
        senha_hash=VerificadorSenhaWerkzeug().gerar_hash(_SENHA)
    )
    app = create_app(
        {
            "TESTING": True,
            "PROPAGATE_EXCEPTIONS": False,
            "JWT_SECRET": _SEGREDO_JWT,
            "DATABASE": str(tmp_path / "anuncios.sqlite3"),
        },
        usuarios=UsuarioRepositoryMemoria([usuario]),
    )

    with app.app_context():
        db = get_db()
        db.execute(
            """
            INSERT INTO usuarios (id, nome, email, matricula, vinculo)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                usuario.id,
                usuario.nome,
                usuario.email,
                usuario.matricula,
                usuario.vinculo.value,
            ),
        )
        db.commit()
        assert db.execute("PRAGMA foreign_keys").fetchone()[0] == 1

    app.add_url_rule(
        "/api/test-forbidden",
        view_func=lambda: abort(403),
        endpoint="test_api_forbidden",
    )
    app.add_url_rule(
        "/api/test-failure",
        view_func=_falha_api,
        endpoint="test_api_failure",
    )

    client = app.test_client()
    login = client.post(
        "/auth/login",
        json={"email": _EMAIL, "senha": _SENHA},
    )
    assert login.status_code == 200
    headers = {
        "Authorization": f"Bearer {login.get_json()['access_token']}"
    }
    return client, headers


def corpo_valido(**overrides):
    corpo = {
        "titulo": "Bicicleta urbana",
        "categoria": "produto",
        "estado_conservacao": "novo",
        "descricao": "Bicicleta revisada e pronta para uso.",
        "preco_a_combinar": False,
        "preco": "10,5",
    }
    corpo.update(overrides)
    return corpo


def test_post_ads_persists_announcement_and_returns_contract(api_client):
    client, headers = api_client

    response = client.post(
        "/api/ads",
        json=corpo_valido(),
        headers=headers,
    )

    assert response.status_code == 201
    assert response.is_json
    result = response.get_json()
    assert set(result) == {
        "id",
        "id_anunciante",
        "nome_anunciante",
        "titulo",
        "categoria",
        "estado_conservacao",
        "descricao",
        "preco",
        "preco_a_combinar",
        "created_at",
    }
    assert result["id_anunciante"] == 1
    assert result["nome_anunciante"] == "Ana"
    assert result["titulo"] == "Bicicleta urbana"
    assert result["preco"] == "10.50"
    assert result["preco_a_combinar"] is False
    assert result["created_at"]


def test_post_ads_uses_only_authenticated_user_and_omits_optional_fields(
    api_client,
):
    client, headers = api_client
    body = {
        "titulo": "Aula de violão",
        "categoria": "servico",
        "descricao": "Aulas para iniciantes.",
        "preco_a_combinar": True,
    }

    response = client.post("/api/ads", json=body, headers=headers)

    assert response.status_code == 201
    result = response.get_json()
    assert result["id_anunciante"] == 1
    assert result["estado_conservacao"] is None
    assert result["preco"] is None
    assert result["preco_a_combinar"] is True


def test_post_ads_supports_event_category(api_client):
    client, headers = api_client
    body = corpo_valido(categoria="evento", preco_a_combinar=True)
    body.pop("estado_conservacao")
    body.pop("preco")

    response = client.post("/api/ads", json=body, headers=headers)

    assert response.status_code == 201
    assert response.get_json()["categoria"] == "evento"
    assert response.get_json()["estado_conservacao"] is None


@pytest.mark.parametrize(
    "media_type",
    ["text/plain", "application/x-www-form-urlencoded"],
)
def test_post_ads_rejects_non_json_with_415(api_client, media_type):
    client, headers = api_client

    response = client.post(
        "/api/ads",
        data="not json",
        content_type=media_type,
        headers=headers,
    )

    assert response.status_code == 415
    assert response.is_json
    assert "erro" in response.get_json()


@pytest.mark.parametrize(
    "body",
    [b"{", b"[]", b"null"],
)
def test_post_ads_rejects_invalid_or_non_object_json_with_400(
    api_client, body
):
    client, headers = api_client

    response = client.post(
        "/api/ads",
        data=body,
        content_type="application/json",
        headers=headers,
    )

    assert response.status_code == 400
    assert response.is_json
    assert "erro" in response.get_json()


def test_post_ads_requires_bearer_auth_and_does_not_redirect(api_client):
    client, _headers = api_client

    response = client.post(
        "/api/ads",
        json=corpo_valido(),
    )

    assert response.status_code == 401
    assert response.is_json
    assert "Location" not in response.headers


def test_post_ads_rejects_body_larger_than_64_kib_as_json(api_client):
    client, headers = api_client

    response = client.post(
        "/api/ads",
        data=b" " * (64 * 1024 + 1),
        content_type="application/json",
        headers=headers,
    )

    assert response.status_code == 413
    assert response.is_json


def test_post_ads_accepts_body_of_exactly_64_kib(api_client):
    client, headers = api_client
    body = json.dumps(corpo_valido(), separators=(",", ":")).encode()
    body += b" " * (64 * 1024 - len(body))

    response = client.post(
        "/api/ads",
        data=body,
        content_type="application/json",
        headers=headers,
    )

    assert response.status_code == 201


@pytest.mark.parametrize("value", ["NaN", "Infinity", "-Infinity"])
def test_post_ads_rejects_non_finite_json_price(api_client, value):
    client, headers = api_client
    body = (
        '{"titulo":"Bicicleta urbana","categoria":"produto",'
        '"estado_conservacao":"novo","descricao":"Em bom estado.",'
        f'"preco_a_combinar":false,"preco":{value}' + "}"
    )

    response = client.post(
        "/api/ads",
        data=body,
        content_type="application/json",
        headers=headers,
    )

    assert response.status_code == 400
    assert response.is_json


@pytest.mark.parametrize(
    "price",
    ["", "-1", "abc", "10.999", "1.234,56", "10000000000"],
)
def test_post_ads_rejects_invalid_price_values(api_client, price):
    client, headers = api_client

    response = client.post(
        "/api/ads",
        json=corpo_valido(preco=price),
        headers=headers,
    )

    assert response.status_code == 422
    assert response.is_json
    assert "preco" in response.get_json()["campos"]


@pytest.mark.parametrize(
    ("price", "expected"),
    [
        ("0", "0.00"),
        ("10", "10.00"),
        ("10,5", "10.50"),
        ("10.50", "10.50"),
        ("9999999999,99", "9999999999.99"),
    ],
)
def test_post_ads_accepts_and_normalizes_prices_without_float_conversion(
    api_client, price, expected
):
    client, headers = api_client

    response = client.post(
        "/api/ads",
        json=corpo_valido(preco=price),
        headers=headers,
    )

    assert response.status_code == 201
    assert response.get_json()["preco"] == expected


@pytest.mark.parametrize(
    ("updates", "field"),
    [
        ({"titulo": "abcd"}, "titulo"),
        ({"titulo": "x" * 81}, "titulo"),
        ({"categoria": "invalida"}, "categoria"),
        ({"descricao": "  "}, "descricao"),
        ({"descricao": "x" * 501}, "descricao"),
        ({"preco_a_combinar": "false"}, "preco_a_combinar"),
        ({"preco_a_combinar": True, "preco": "0"}, "preco"),
    ],
)
def test_post_ads_validates_required_fields_and_limits(
    api_client, updates, field
):
    client, headers = api_client

    response = client.post(
        "/api/ads",
        json=corpo_valido(**updates),
        headers=headers,
    )

    assert response.status_code == 422
    assert field in response.get_json()["campos"]


def test_post_ads_trims_title_and_description(api_client):
    client, headers = api_client

    response = client.post(
        "/api/ads",
        json=corpo_valido(
            titulo="  Bicicleta urbana  ",
            descricao="  Em ótimo estado.  ",
        ),
        headers=headers,
    )

    assert response.status_code == 201
    assert response.get_json()["titulo"] == "Bicicleta urbana"
    assert response.get_json()["descricao"] == "Em ótimo estado."


def test_post_ads_rejects_json_number_for_price(api_client):
    client, headers = api_client
    body = (
        '{"titulo":"Bicicleta urbana","categoria":"produto",'
        '"estado_conservacao":"novo","descricao":"Em bom estado.",'
        '"preco_a_combinar":false,"preco":10.5}'
    )

    response = client.post(
        "/api/ads",
        data=body,
        content_type="application/json",
        headers=headers,
    )

    assert response.status_code == 422
    assert "preco" in response.get_json()["campos"]


@pytest.mark.parametrize(
    "category_fields",
    [
        {"categoria": "produto"},
        {"categoria": "servico", "estado_conservacao": "novo"},
        {"categoria": "evento", "estado_conservacao": "usado_regular"},
    ],
)
def test_post_ads_validates_conservation_state_by_category(
    api_client, category_fields
):
    client, headers = api_client
    body = corpo_valido(**category_fields)
    if category_fields["categoria"] == "produto":
        body.pop("estado_conservacao")

    response = client.post(
        "/api/ads",
        json=body,
        headers=headers,
    )

    assert response.status_code == 422
    assert response.is_json
    assert "estado_conservacao" in response.get_json()["campos"]


@pytest.mark.parametrize("field", ["id", "id_anunciante", "created_at"])
def test_post_ads_rejects_server_owned_fields(api_client, field):
    client, headers = api_client

    response = client.post(
        "/api/ads",
        json=corpo_valido(**{field: 10}),
        headers=headers,
    )

    assert response.status_code == 422
    assert "geral" in response.get_json()["campos"]


@pytest.mark.parametrize(
    ("path", "expected_status"),
    [
        ("/api", 404),
        ("/api/not-found", 404),
        ("/api/ads", 405),
        ("/api/test-forbidden", 403),
        ("/api/test-failure", 500),
    ],
)
def test_api_http_errors_are_json(api_client, path, expected_status):
    client, _headers = api_client

    response = client.get(path)

    assert response.status_code == expected_status
    assert response.is_json
    assert "erro" in response.get_json()
    if expected_status == 500:
        assert "detalhe interno não deve ser exposto" not in response.get_data(
            as_text=True
        )
