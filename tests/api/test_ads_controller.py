from io import BytesIO
from datetime import datetime, timedelta, timezone

import pytest
from werkzeug.security import generate_password_hash

from server.app import create_app
from server.core.entities.anunciante import Anunciante
from server.core.entities.contato import Contato
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


def create_ads_app(image_root=None):
    config = {
        "DATABASE_URL": "sqlite:///:memory:",
        "CORS_ORIGINS": [],
    }
    if image_root is not None:
        config["STORAGE_LOCAL_ROOT"] = str(image_root)
    app = create_app(
        config
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


def complete_advertiser_profile(app):
    app.extensions["anunciante_repository"].salvar(
        Anunciante(
            usuario_id=1,
            nome_exibicao="Ana Vendas",
            contatos=(Contato.criar("email", "ana@example.com"),),
        )
    )


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
            "Tipo deve ser all, product, service ou event.",
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
    assert response.json == {"message": message}
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
        "message": "Erro interno ao buscar anúncios.",
    }
    assert "SQLSTATE" not in response.get_data(as_text=True)
    app.extensions["database_engine"].dispose()


def test_publish_requires_a_real_complete_advertiser_profile():
    app = create_ads_app()
    headers = app.extensions["test_auth_headers"]

    response = app.test_client().post(
        "/api/ads",
        json={
            "titulo": "Bicicleta urbana",
            "categoria": "produto",
            "estado_conservacao": "novo",
            "descricao": "Revisada e pronta para uso.",
            "preco": 850.00,
        },
        headers=headers,
    )

    assert response.status_code == 403
    assert response.json["code"] == "perfil_incompleto"
    with app.extensions["session_factory"]() as session:
        assert session.query(AdModel).count() == 2
    app.extensions["database_engine"].dispose()


def test_publish_is_visible_in_feed_with_real_profile_name():
    app = create_ads_app()
    complete_advertiser_profile(app)
    headers = app.extensions["test_auth_headers"]
    client = app.test_client()

    response = client.post(
        "/api/ads",
        json={
            "titulo": "Bicicleta urbana",
            "categoria": "produto",
            "estado_conservacao": "usado_regular",
            "descricao": "Revisada e pronta para uso.",
            "preco": 850.25,
        },
        headers=headers,
    )
    feed = client.get("/api/ads", headers=headers)

    assert response.status_code == 201
    assert response.json["nome_anunciante"] == "Ana Vendas"
    assert response.json["type"] == "product"
    assert response.json["category"] == "produto"
    assert response.json["price"] == 850.25
    assert response.json["preco_a_combinar"] is False
    assert response.json["created_at"]
    instante_criacao = datetime.fromisoformat(
        response.json["created_at"].replace("Z", "+00:00")
    )
    assert instante_criacao.utcoffset() == timedelta(0)
    assert feed.status_code == 200
    assert feed.json["items"][0]["title"] == "Bicicleta urbana"
    assert (
        feed.json["items"][0]["created_at"].removesuffix("Z")
        == response.json["created_at"].removesuffix("Z")
    )
    with app.extensions["session_factory"]() as session:
        published = (
            session.query(AdModel)
            .filter(
                AdModel.title == "Bicicleta urbana",
                AdModel.usuario_id == 1,
            )
            .one()
        )
        assert published.expires_at - published.created_at == timedelta(
            days=30
        )
    app.extensions["database_engine"].dispose()


def test_publish_supports_service_without_conservation_state():
    app = create_ads_app()
    complete_advertiser_profile(app)
    response = app.test_client().post(
        "/api/ads",
        json={
            "titulo": "Aulas de inglês",
            "categoria": "servico",
            "descricao": "Aulas particulares para iniciantes.",
            "preco": 50,
        },
        headers=app.extensions["test_auth_headers"],
    )

    assert response.status_code == 201
    assert response.json["type"] == "service"
    assert response.json["category"] == "servico"
    assert response.json["estado_conservacao"] is None
    app.extensions["database_engine"].dispose()


def test_event_and_negotiable_price_are_supported_by_the_feed():
    app = create_ads_app()
    complete_advertiser_profile(app)
    headers = app.extensions["test_auth_headers"]
    client = app.test_client()

    response = client.post(
        "/api/ads",
        json={
            "titulo": "Feira comunitária",
            "categoria": "evento",
            "descricao": "Evento aberto à comunidade.",
            "preco_a_combinar": True,
        },
        headers=headers,
    )
    feed = client.get(
        "/api/ads",
        query_string={"type": "event"},
        headers=headers,
    )

    assert response.status_code == 201
    assert response.json["type"] == "event"
    assert response.json["price"] is None
    assert response.json["preco_a_combinar"] is True
    assert feed.status_code == 200
    assert [ad["title"] for ad in feed.json["items"]] == [
        "Feira comunitária",
    ]
    app.extensions["database_engine"].dispose()


def test_publish_reports_invalid_title_on_the_field():
    app = create_ads_app()
    complete_advertiser_profile(app)

    response = app.test_client().post(
        "/api/ads",
        json={
            "titulo": "abc",
            "categoria": "produto",
            "estado_conservacao": "novo",
            "descricao": "Descrição válida.",
            "preco": 10,
        },
        headers=app.extensions["test_auth_headers"],
    )

    assert response.status_code == 422
    assert "titulo" in response.json["campos"]
    app.extensions["database_engine"].dispose()


def test_publish_stores_an_image_and_exposes_it_from_local_storage(tmp_path):
    app = create_ads_app(tmp_path / "media")
    complete_advertiser_profile(app)

    response = app.test_client().post(
        "/api/ads",
        data={
            "titulo": "Cartaz do evento",
            "categoria": "evento",
            "descricao": "Evento aberto à comunidade.",
            "preco": "0",
            "imagem": (
                BytesIO(b"\x89PNG\r\n\x1a\nconteudo"),
                "cartaz.png",
            ),
        },
        headers=app.extensions["test_auth_headers"],
    )

    assert response.status_code == 201
    image_url = response.json["image_url"]
    image = app.test_client().get(image_url)
    assert image.status_code == 200
    assert image.mimetype == "image/png"
    assert image.data == b"\x89PNG\r\n\x1a\nconteudo"
    app.extensions["database_engine"].dispose()


def test_publish_allows_ad_images_larger_than_profile_request_limit(
    tmp_path,
):
    app = create_ads_app(tmp_path / "media")
    complete_advertiser_profile(app)
    image = b"\x89PNG\r\n\x1a\n" + b"x" * (3 * 1024 * 1024)

    response = app.test_client().post(
        "/api/ads",
        data={
            "titulo": "Cartaz grande",
            "categoria": "evento",
            "descricao": "Evento aberto à comunidade.",
            "preco": "0",
            "imagem": (BytesIO(image), "cartaz.png"),
        },
        headers=app.extensions["test_auth_headers"],
    )

    assert response.status_code == 201
    app.extensions["database_engine"].dispose()


def test_publish_checks_profile_before_parsing_the_request_body():
    app = create_ads_app()
    response = app.test_client().post(
        "/api/ads",
        data="{",
        content_type="application/json",
        headers=app.extensions["test_auth_headers"],
    )

    assert response.status_code == 403
    assert response.is_json
    assert response.json["code"] == "perfil_incompleto"
    with app.extensions["session_factory"]() as session:
        assert session.query(AdModel).count() == 2
    app.extensions["database_engine"].dispose()


def test_publish_rejects_identity_and_unknown_fields_from_the_client():
    app = create_ads_app()
    complete_advertiser_profile(app)
    dados = {
        "titulo": "Caderno novo",
        "categoria": "produto",
        "estado_conservacao": "novo",
        "descricao": "Sem uso.",
        "preco": 10,
        "id": 8,
        "id_anunciante": 99,
        "created_at": "2026-01-01T00:00:00Z",
        "nome_anunciante": "Outra pessoa",
        "campo_desconhecido": "valor",
    }

    response = app.test_client().post(
        "/api/ads",
        json=dados,
        headers=app.extensions["test_auth_headers"],
    )

    assert response.status_code == 422
    for campo in (
        "id",
        "id_anunciante",
        "created_at",
        "nome_anunciante",
        "campo_desconhecido",
    ):
        assert campo in response.json["campos"]
    with app.extensions["session_factory"]() as session:
        assert session.query(AdModel).count() == 2
    app.extensions["database_engine"].dispose()


def test_publish_requires_a_boolean_for_negotiable_price_in_json():
    app = create_ads_app()
    complete_advertiser_profile(app)
    response = app.test_client().post(
        "/api/ads",
        json={
            "titulo": "Feira comunitária",
            "categoria": "evento",
            "descricao": "Evento aberto à comunidade.",
            "preco_a_combinar": "true",
        },
        headers=app.extensions["test_auth_headers"],
    )

    assert response.status_code == 422
    assert "preco_a_combinar" in response.json["campos"]
    with app.extensions["session_factory"]() as session:
        assert session.query(AdModel).count() == 2
    app.extensions["database_engine"].dispose()


@pytest.mark.parametrize("preco", ["NaN", "Infinity", "-Infinity"])
def test_publish_reports_non_finite_json_prices_on_the_price_field(preco):
    app = create_ads_app()
    complete_advertiser_profile(app)
    body = (
        '{"titulo":"Feira comunitária","categoria":"evento",'
        '"descricao":"Evento aberto à comunidade.","preco":'
        f"{preco}"
        "}"
    )
    response = app.test_client().post(
        "/api/ads",
        data=body,
        content_type="application/json",
        headers=app.extensions["test_auth_headers"],
    )

    assert response.status_code == 422
    assert "preco" in response.json["campos"]
    with app.extensions["session_factory"]() as session:
        assert session.query(AdModel).count() == 2
    app.extensions["database_engine"].dispose()


def test_publish_keeps_multipart_form_boolean_compatibility():
    app = create_ads_app()
    complete_advertiser_profile(app)
    response = app.test_client().post(
        "/api/ads",
        data={
            "titulo": "Feira comunitária",
            "categoria": "evento",
            "descricao": "Evento aberto à comunidade.",
            "preco_a_combinar": "true",
        },
        content_type="multipart/form-data",
        headers=app.extensions["test_auth_headers"],
    )

    assert response.status_code == 201
    assert response.json["preco_a_combinar"] is True
    assert response.json["price"] is None
    app.extensions["database_engine"].dispose()


def test_publish_rejects_json_larger_than_64_kib_as_json_413():
    app = create_ads_app()
    complete_advertiser_profile(app)
    body = '{"extra":"' + ("x" * (64 * 1024)) + '"}'
    response = app.test_client().post(
        "/api/ads",
        data=body,
        content_type="application/json",
        headers=app.extensions["test_auth_headers"],
    )

    assert response.status_code == 413
    assert response.is_json
    with app.extensions["session_factory"]() as session:
        assert session.query(AdModel).count() == 2
    app.extensions["database_engine"].dispose()


@pytest.mark.parametrize(
    ("method", "path", "status"),
    [
        ("get", "/api/rota-inexistente", 404),
        ("patch", "/api/ads", 405),
    ],
)
def test_api_http_errors_are_json(method, path, status):
    app = create_ads_app()
    response = getattr(app.test_client(), method)(path)

    assert response.status_code == status
    assert response.is_json
    assert "message" in response.json
    app.extensions["database_engine"].dispose()


def test_unexpected_api_failure_returns_generic_json_without_details(
    monkeypatch,
):
    app = create_ads_app()
    repository = app.extensions["anunciante_repository"]

    def fail_repository(*args, **kwargs):
        raise RuntimeError("private database connection detail")

    monkeypatch.setattr(repository, "buscar_por_usuario_id", fail_repository)
    response = app.test_client().post(
        "/api/ads",
        json={},
        headers=app.extensions["test_auth_headers"],
    )

    assert response.status_code == 500
    assert response.is_json
    assert response.json == {
        "message": "Erro interno ao processar a requisição.",
    }
    assert "private database connection detail" not in response.get_data(
        as_text=True
    )
    app.extensions["database_engine"].dispose()


def test_publish_rejects_non_json_content_type_with_json_error():
    app = create_ads_app()
    complete_advertiser_profile(app)
    response = app.test_client().post(
        "/api/ads",
        data="{}",
        content_type="text/plain",
        headers=app.extensions["test_auth_headers"],
    )

    assert response.status_code == 415
    assert response.is_json
    app.extensions["database_engine"].dispose()


def test_publish_rejects_malformed_json_with_json_error():
    app = create_ads_app()
    complete_advertiser_profile(app)
    response = app.test_client().post(
        "/api/ads",
        data="{",
        content_type="application/json",
        headers=app.extensions["test_auth_headers"],
    )

    assert response.status_code == 400
    assert response.is_json
    app.extensions["database_engine"].dispose()


def test_publish_requires_authentication_and_returns_json_401():
    app = create_ads_app()
    response = app.test_client().post("/api/ads", json={})

    assert response.status_code == 401
    assert response.is_json
    assert response.json == {"message": "Sessão inválida ou expirada."}
    app.extensions["database_engine"].dispose()
