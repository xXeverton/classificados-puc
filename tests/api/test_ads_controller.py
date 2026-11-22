from datetime import datetime, timezone

import pytest
from werkzeug.security import generate_password_hash

from server.app import create_app
from server.infra.db.database import create_session_factory
from server.infra.db.models import AdModel, UsuarioModel


def add_confirmed_user_and_login(app):
    session_factory = create_session_factory(app.extensions["database_engine"])
    with session_factory.begin() as session:
        session.add(
            UsuarioModel(
                nome="Ana",
                email="ana@aluno.puc-rio.br",
                nome_usuario="ana123",
                matricula="123",
                vinculo="aluno",
                senha_hash=generate_password_hash("Senha123"),
                confirmado_em=datetime.now(timezone.utc),
            )
        )
    login = app.test_client().post(
        "/auth/login",
        json={
            "identificador": "ana@aluno.puc-rio.br",
            "senha": "Senha123",
        },
    )
    assert login.status_code == 200
    return {"Authorization": f"Bearer {login.json['token']}"}


def create_ads_app():
    app = create_app(
        {
            "DATABASE_URL": "sqlite:///:memory:",
            "CORS_ORIGINS": [],
        }
    )
    headers = add_confirmed_user_and_login(app)
    app.extensions["test_auth_headers"] = headers
    session_factory = create_session_factory(
        app.extensions["database_engine"]
    )
    with session_factory.begin() as session:
        session.add_all(
            [
                AdModel(
                    title="Bicicleta urbana",
                    description="Ideal para deslocamentos na universidade.",
                    type="product",
                    category="Veículos",
                    price=450.0,
                    image_url="https://example.com/bike.jpg",
                    created_at=datetime(
                        2026,
                        11,
                        12,
                        10,
                        0,
                        tzinfo=timezone.utc,
                    ),
                    status="published",
                ),
                AdModel(
                    title="Aulas de inglês",
                    description="Aulas particulares por hora.",
                    type="service",
                    category="Educação",
                    price=80.0,
                    image_url=None,
                    created_at=datetime(
                        2026,
                        11,
                        11,
                        10,
                        0,
                        tzinfo=timezone.utc,
                    ),
                    status="published",
                ),
            ]
        )
    return app


def test_get_ads_returns_paginated_cards_with_public_fields():
    app = create_ads_app()

    response = app.test_client().get(
        "/api/ads",
        headers=app.extensions["test_auth_headers"],
    )

    assert response.status_code == 200
    assert response.json["page"] == 1
    assert response.json["per_page"] == 20
    assert response.json["total_items"] == 2
    assert response.json["total_pages"] == 1
    assert response.json["items"][0]["title"] == "Bicicleta urbana"
    assert response.json["items"][0]["description"] == (
        "Ideal para deslocamentos na universidade."
    )
    assert response.json["items"][0]["type"] == "product"
    assert response.json["items"][0]["category"] == "Veículos"
    assert response.json["items"][0]["price"] == 450.0
    assert response.json["items"][0]["image_url"] == (
        "https://example.com/bike.jpg"
    )
    assert "created_at" in response.json["items"][0]
    app.extensions["database_engine"].dispose()


def test_get_ads_filters_by_search():
    app = create_ads_app()

    response = app.test_client().get(
        "/api/ads",
        query_string={"search": "UNIVERSIDADE"},
        headers=app.extensions["test_auth_headers"],
    )

    assert response.status_code == 200
    assert [item["title"] for item in response.json["items"]] == [
        "Bicicleta urbana",
    ]
    app.extensions["database_engine"].dispose()


def test_get_ads_filters_by_service_type():
    app = create_ads_app()

    response = app.test_client().get(
        "/api/ads",
        query_string={"type": "service"},
        headers=app.extensions["test_auth_headers"],
    )

    assert response.status_code == 200
    assert [item["title"] for item in response.json["items"]] == [
        "Aulas de inglês",
    ]
    app.extensions["database_engine"].dispose()


def test_get_ads_returns_empty_feed_message():
    app = create_app(
        {
            "DATABASE_URL": "sqlite:///:memory:",
            "CORS_ORIGINS": [],
        }
    )
    headers = add_confirmed_user_and_login(app)

    response = app.test_client().get("/api/ads", headers=headers)

    assert response.status_code == 200
    assert response.json == {
        "items": [],
        "page": 1,
        "per_page": 20,
        "total_pages": 0,
        "total_items": 0,
        "message": "Nenhum anúncio publicado encontrado.",
    }
    app.extensions["database_engine"].dispose()


def test_get_ads_accepts_missing_optional_parameters():
    app = create_ads_app()

    response = app.test_client().get(
        "/api/ads",
        headers=app.extensions["test_auth_headers"],
    )

    assert response.status_code == 200
    app.extensions["database_engine"].dispose()


@pytest.mark.parametrize(
    ("query_string", "message"),
    [
        (
            {"page": "0"},
            "Página deve ser um inteiro positivo.",
        ),
        (
            {"page": "abc"},
            "Página deve ser um inteiro positivo.",
        ),
        (
            {"type": "invalid"},
            "Tipo deve ser all, product ou service.",
        ),
    ],
)
def test_get_ads_rejects_invalid_parameters(query_string, message):
    app = create_ads_app()

    response = app.test_client().get(
        "/api/ads",
        query_string=query_string,
        headers=app.extensions["test_auth_headers"],
    )

    assert response.status_code == 400
    assert response.json == {"code": None, "message": message}
    app.extensions["database_engine"].dispose()


def test_get_ads_rejects_unauthenticated_user():
    app = create_app(
        {
            "DATABASE_URL": "sqlite:///:memory:",
            "CORS_ORIGINS": [],
        }
    )
    response = app.test_client().get("/api/ads")

    assert response.status_code == 401
    assert response.get_json() == {
        "message": "Sessão inválida ou expirada.",
    }
    app.extensions["database_engine"].dispose()


def test_get_ads_returns_500_without_sql_details_when_repository_fails(
    monkeypatch,
):
    app = create_ads_app()
    repository = app.extensions["ad_repository"]

    def fail_repository(*args, **kwargs):
        raise RuntimeError(
            "SQLSTATE private database connection error",
        )

    monkeypatch.setattr(
        repository,
        "list_published",
        fail_repository,
    )

    response = app.test_client().get(
        "/api/ads",
        headers=app.extensions["test_auth_headers"],
    )

    assert response.status_code == 500
    assert response.json == {
        "code": None,
        "message": "Erro interno ao buscar anúncios.",
    }
    assert "SQLSTATE" not in response.get_data(as_text=True)
    app.extensions["database_engine"].dispose()


def get_ads(app, **query):
    return app.test_client().get(
        "/api/ads",
        query_string=query,
        headers=app.extensions["test_auth_headers"],
    )


def test_get_ads_filters_by_category():
    app = create_ads_app()

    response = get_ads(app, category="educação")

    assert response.status_code == 200
    assert [item["title"] for item in response.json["items"]] == [
        "Aulas de inglês",
    ]
    app.extensions["database_engine"].dispose()


def test_get_ads_filters_by_price_range():
    app = create_ads_app()

    cheap = get_ads(app, max_price="80")
    expensive = get_ads(app, min_price="80.01", max_price="450")

    assert [item["title"] for item in cheap.json["items"]] == [
        "Aulas de inglês",
    ]
    assert [item["title"] for item in expensive.json["items"]] == [
        "Bicicleta urbana",
    ]
    app.extensions["database_engine"].dispose()


def test_get_ads_combines_filters_and_reports_empty_result():
    app = create_ads_app()

    response = get_ads(
        app, search="bicicleta", category="Veículos", max_price="100"
    )

    assert response.status_code == 200
    assert response.json["items"] == []
    assert response.json["message"] == "Nenhum anúncio publicado encontrado."
    app.extensions["database_engine"].dispose()


@pytest.mark.parametrize(
    ("query", "message"),
    [
        ({"min_price": "abc"}, "Preço mínimo deve ser um número."),
        ({"max_price": "10,5"}, "Preço máximo deve ser um número."),
        ({"max_price": "nan"}, "Preço máximo deve ser um número."),
        ({"min_price": "-1"}, "Preço mínimo não pode ser negativo."),
        (
            {"min_price": "100", "max_price": "50"},
            "Preço mínimo não pode ser maior que o máximo.",
        ),
    ],
)
def test_get_ads_rejects_invalid_price(query, message):
    app = create_ads_app()

    response = get_ads(app, **query)

    assert response.status_code == 400
    assert response.json["message"] == message
    app.extensions["database_engine"].dispose()
