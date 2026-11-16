import json
from datetime import timedelta

import pytest
from flask import abort

from app.database import get_db
from app.main import create_app
from infra.repositories.memoria import UsuarioRepositoryMemoria
from infra.repositories.perfil_anunciante_mock import (
    PerfilAnuncianteMock,
    VerificadorPerfilCompletoMock,
)
from infra.seguranca.verificador_senha_werkzeug import (
    VerificadorSenhaWerkzeug,
)
from infra.seguranca.servico_token_jwt import ServicoTokenJwt
from tests.fakes import RelogioControlado, criar_usuario
from use_cases.verificar_perfil_completo import (
    CHAVE_EXTENSAO_PERFIL_COMPLETO,
)

_EMAIL = "ana@aluno.puc-rio.br"
_SENHA = "senha-correta"
_SEGREDO_JWT = "segredo-de-teste-com-tamanho-suficiente"


def _falha_api():
    raise RuntimeError("detalhe interno não deve ser exposto")


def criar_app_api(tmp_path, usuarios):
    perfis = {
        usuario.id: PerfilAnuncianteMock(
            nome_exibicao=usuario.nome,
            foto="mock://foto-temporaria",
            whatsapp="+5521999999999",
            email=usuario.email,
        )
        for usuario in usuarios
    }
    app = create_app(
        {
            "TESTING": True,
            "PROPAGATE_EXCEPTIONS": False,
            "JWT_SECRET": _SEGREDO_JWT,
            "DATABASE": str(tmp_path / "anuncios.sqlite3"),
        },
        usuarios=UsuarioRepositoryMemoria(usuarios),
        verificador_perfil=VerificadorPerfilCompletoMock(perfis),
    )

    with app.app_context():
        db = get_db()
        for usuario in usuarios:
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
    return app


def cabecalho_autenticacao(client, email=_EMAIL):
    login = client.post(
        "/auth/login",
        json={"email": email, "senha": _SENHA},
    )
    assert login.status_code == 200
    return {
        "Authorization": f"Bearer {login.get_json()['access_token']}"
    }


@pytest.fixture
def api_client(tmp_path):
    usuario = criar_usuario(
        senha_hash=VerificadorSenhaWerkzeug().gerar_hash(_SENHA)
    )
    app = criar_app_api(tmp_path, [usuario])

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
    return client, cabecalho_autenticacao(client)


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
    assert result["created_at"].endswith("Z")

    with client.application.app_context():
        database = get_db()
        anuncio = database.execute(
            "SELECT id, preco FROM anuncios WHERE id = ?",
            (result["id"],),
        ).fetchone()
        feed_topo = database.execute(
            """
            SELECT a.id, u.nome
            FROM anuncios AS a
            JOIN usuarios AS u ON u.id = a.id_anunciante
            ORDER BY a.created_at DESC
            LIMIT 1
            """
        ).fetchone()
    assert anuncio["preco"] == 10.5
    assert feed_topo["id"] == result["id"]
    assert feed_topo["nome"] == "Ana"


def test_post_ads_rolls_back_insert_if_readback_fails(api_client):
    client, headers = api_client

    with client.application.app_context():
        database = get_db()
        database.executescript(
            """
            CREATE TRIGGER remove_inserted_announcement
            AFTER INSERT ON anuncios
            BEGIN
                DELETE FROM anuncios WHERE id = NEW.id;
            END;
            """
        )
        database.commit()

    response = client.post(
        "/api/ads",
        json=corpo_valido(),
        headers=headers,
    )

    assert response.status_code == 500
    assert response.is_json
    assert response.get_json() == {"erro": "Erro interno do servidor."}
    with client.application.app_context():
        assert get_db().execute(
            "SELECT COUNT(*) FROM anuncios"
        ).fetchone()[0] == 0


def test_post_ads_uses_parameters_for_client_text(api_client):
    client, headers = api_client

    response = client.post(
        "/api/ads",
        json=corpo_valido(
            titulo="Bike'); DROP TABLE anuncios;--",
            descricao="Texto '); DROP TABLE usuarios;--",
        ),
        headers=headers,
    )

    assert response.status_code == 201
    assert response.get_json()["titulo"] == "Bike'); DROP TABLE anuncios;--"
    with client.application.app_context():
        database = get_db()
        assert database.execute(
            "SELECT 1 FROM sqlite_master "
            "WHERE type = 'table' AND name = 'anuncios'"
        ).fetchone() is not None
        assert database.execute(
            "SELECT 1 FROM usuarios WHERE id = ?", (1,)
        ).fetchone() is not None

    response = client.post(
        "/api/ads",
        json=corpo_valido(preco="10; DROP TABLE anuncios"),
        headers=headers,
    )
    assert response.status_code == 422
    assert "preco" in response.get_json()["campos"]


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


def test_post_ads_defaults_preco_a_combinar_to_false(api_client):
    client, headers = api_client
    body = corpo_valido()
    body.pop("preco_a_combinar")

    response = client.post("/api/ads", json=body, headers=headers)

    assert response.status_code == 201
    assert response.get_json()["preco_a_combinar"] is False


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("titulo", "x" * 5),
        ("titulo", "x" * 80),
        ("descricao", "x" * 500),
    ],
)
def test_post_ads_accepts_text_field_boundaries(api_client, field, value):
    client, headers = api_client

    response = client.post(
        "/api/ads",
        json=corpo_valido(**{field: value}),
        headers=headers,
    )

    assert response.status_code == 201


@pytest.mark.parametrize(
    "field",
    ("titulo", "categoria", "descricao", "preco"),
)
def test_post_ads_rejects_missing_required_fields(api_client, field):
    client, headers = api_client
    body = corpo_valido()
    body.pop(field, None)

    response = client.post("/api/ads", json=body, headers=headers)

    assert response.status_code == 422
    assert field in response.get_json()["campos"]


def test_post_ads_allows_null_price_when_preco_a_combinar(api_client):
    client, headers = api_client

    response = client.post(
        "/api/ads",
        json=corpo_valido(preco_a_combinar=True, preco=None),
        headers=headers,
    )

    assert response.status_code == 201
    assert response.get_json()["preco"] is None


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


def test_post_ads_rejects_invalid_bearer_token(api_client):
    client, _headers = api_client

    response = client.post(
        "/api/ads",
        json=corpo_valido(),
        headers={"Authorization": "Bearer token-invalido"},
    )

    assert response.status_code == 401
    assert response.is_json
    assert "Location" not in response.headers


def test_post_ads_rejects_expired_bearer_token(api_client):
    client, _headers = api_client
    token_expirado = ServicoTokenJwt(
        segredo=_SEGREDO_JWT,
        validade=timedelta(seconds=1),
        relogio=RelogioControlado(),
    ).emitir(1)

    response = client.post(
        "/api/ads",
        json=corpo_valido(),
        headers={"Authorization": f"Bearer {token_expirado.token}"},
    )

    assert response.status_code == 401
    assert response.is_json
    assert "Location" not in response.headers


def test_default_profile_mock_fails_closed():
    app = create_app(
        {
            "TESTING": True,
            "JWT_SECRET": _SEGREDO_JWT,
        }
    )
    verificador = app.extensions[CHAVE_EXTENSAO_PERFIL_COMPLETO]

    assert not verificador.esta_completo(1)


def test_post_ads_requires_complete_mock_profile_before_reading_body(
    api_client,
):
    client, headers = api_client
    verificador = client.application.extensions[
        CHAVE_EXTENSAO_PERFIL_COMPLETO
    ]
    verificador.definir_perfil(
        1,
        PerfilAnuncianteMock(
            nome_exibicao="Ana",
            foto="mock://foto-temporaria",
            whatsapp=None,
            email=_EMAIL,
        ),
    )

    for data, content_type in (
        (b'{"titulo":"Bicicleta urbana"}', "application/json"),
        (b"{", "application/json"),
        (b"not json", "text/plain"),
    ):
        response = client.post(
            "/api/ads",
            data=data,
            content_type=content_type,
            headers=headers,
        )

        assert response.status_code == 403
        assert response.get_json()["codigo"] == "perfil_incompleto"

    with client.application.app_context():
        assert get_db().execute(
            "SELECT COUNT(*) FROM anuncios"
        ).fetchone()[0] == 0


def test_post_ads_returns_401_when_authenticated_user_is_not_in_database(
    api_client,
):
    client, headers = api_client

    with client.application.app_context():
        database = get_db()
        database.execute("DELETE FROM usuarios WHERE id = ?", (1,))
        database.commit()

    response = client.post(
        "/api/ads",
        json=corpo_valido(),
        headers=headers,
    )

    assert response.status_code == 401
    assert response.is_json
    with client.application.app_context():
        assert get_db().execute(
            "SELECT COUNT(*) FROM anuncios"
        ).fetchone()[0] == 0


def test_post_ads_keeps_each_authenticated_user_as_advertiser(tmp_path):
    usuario_ana = criar_usuario(
        senha_hash=VerificadorSenhaWerkzeug().gerar_hash(_SENHA)
    )
    usuario_bia = criar_usuario(
        id=2,
        nome="Bia",
        email="bia@aluno.puc-rio.br",
        matricula="2310002",
        senha_hash=VerificadorSenhaWerkzeug().gerar_hash(_SENHA),
    )
    app = criar_app_api(tmp_path, [usuario_ana, usuario_bia])
    client = app.test_client()

    for usuario in (usuario_ana, usuario_bia):
        response = client.post(
            "/api/ads",
            json=corpo_valido(),
            headers=cabecalho_autenticacao(client, usuario.email),
        )
        assert response.status_code == 201
        assert response.get_json()["id_anunciante"] == usuario.id


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
    ("price", "expected"),
    [
        ("0", "0.00"),
        ("10", "10.00"),
        ("10.5", "10.50"),
        ("10.50", "10.50"),
        ("9999999999.99", "9999999999.99"),
    ],
)
def test_post_ads_accepts_json_numbers_without_float_conversion(
    api_client, price, expected
):
    client, headers = api_client
    body = (
        '{"titulo":"Bicicleta urbana","categoria":"produto",'
        '"estado_conservacao":"novo","descricao":"Em bom estado.",'
        f'"preco":{price}' + "}"
    )

    response = client.post(
        "/api/ads",
        data=body,
        content_type="application/json",
        headers=headers,
    )

    assert response.status_code == 201
    assert response.get_json()["preco"] == expected


@pytest.mark.parametrize(
    ("updates", "field"),
    [
        ({"titulo": "abcd"}, "titulo"),
        ({"titulo": "   "}, "titulo"),
        ({"titulo": "x" * 81}, "titulo"),
        ({"categoria": "invalida"}, "categoria"),
        ({"descricao": ""}, "descricao"),
        ({"descricao": "  "}, "descricao"),
        ({"descricao": "x" * 501}, "descricao"),
        ({"preco_a_combinar": "false"}, "preco_a_combinar"),
        ({"preco_a_combinar": True, "preco": "0"}, "preco"),
        ({"preco": True}, "preco"),
        ({"titulo": 123}, "titulo"),
        ({"descricao": []}, "descricao"),
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


def test_post_ads_trims_title_and_preserves_description(api_client):
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
    assert response.get_json()["descricao"] == "  Em ótimo estado.  "


def test_post_ads_trims_only_ascii_spaces_from_title(api_client):
    client, headers = api_client

    response = client.post(
        "/api/ads",
        json=corpo_valido(titulo="\u00a0Bicicleta urbana\u00a0"),
        headers=headers,
    )

    assert response.status_code == 201
    assert response.get_json()["titulo"] == "\u00a0Bicicleta urbana\u00a0"


@pytest.mark.parametrize("categoria", ["servico", "evento"])
def test_post_ads_allows_null_conservation_state_for_non_products(
    api_client, categoria
):
    client, headers = api_client

    response = client.post(
        "/api/ads",
        json=corpo_valido(
            categoria=categoria,
            estado_conservacao=None,
            preco_a_combinar=True,
            preco=None,
        ),
        headers=headers,
    )

    assert response.status_code == 201
    assert response.get_json()["estado_conservacao"] is None


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


@pytest.mark.parametrize(
    "field",
    ["id", "id_anunciante", "created_at", "nome_anunciante", "campo_extra"],
)
def test_post_ads_rejects_server_owned_fields(api_client, field):
    client, headers = api_client

    response = client.post(
        "/api/ads",
        json=corpo_valido(**{field: 10}),
        headers=headers,
    )

    assert response.status_code == 422
    assert field in response.get_json()["campos"]


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
