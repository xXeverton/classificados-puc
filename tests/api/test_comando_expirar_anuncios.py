from datetime import UTC, datetime, timedelta

from server.app import create_app
from server.infra.db.database import create_session_factory
from server.infra.db.models import AdModel
from tests.api.test_ads_controller import add_confirmed_user_and_login
from tests.core.usecases.fakes import RelogioFalso

NOW = datetime(2026, 12, 15, 12, 0, tzinfo=UTC)


def make_ad_model(title, created_at, status="published"):
    return AdModel(
        title=title,
        description="Anúncio de teste.",
        type="product",
        category="Livros",
        price=10.0,
        image_url=None,
        created_at=created_at,
        status=status,
        expires_at=None,
    )


def create_app_with_ads(ads):
    app = create_app(
        {
            "DATABASE_URL": "sqlite:///:memory:",
            "CORS_ORIGINS": [],
            "RELOGIO": RelogioFalso(NOW),
        }
    )
    session_factory = create_session_factory(
        app.extensions["database_engine"]
    )
    with session_factory.begin() as session:
        session.add_all(ads)
    return app


def feed_titles(app, headers):
    response = app.test_client().get("/api/ads", headers=headers)
    assert response.status_code == 200
    return [item["title"] for item in response.json["items"]]


def test_command_expires_overdue_ads_and_removes_them_from_feed():
    app = create_app_with_ads(
        [
            make_ad_model("Vencido", NOW - timedelta(days=31)),
            make_ad_model("Em dia", NOW - timedelta(days=3)),
        ]
    )
    headers = add_confirmed_user_and_login(app)
    assert sorted(feed_titles(app, headers)) == ["Em dia", "Vencido"]

    result = app.test_cli_runner().invoke(args=["expirar-anuncios"])

    assert result.exit_code == 0
    assert "1 anúncio(s) expirado(s)." in result.output
    assert feed_titles(app, headers) == ["Em dia"]


def test_command_reports_zero_when_nothing_is_overdue():
    app = create_app_with_ads(
        [make_ad_model("Em dia", NOW - timedelta(days=3))]
    )

    result = app.test_cli_runner().invoke(args=["expirar-anuncios"])

    assert result.exit_code == 0
    assert "0 anúncio(s) expirado(s)." in result.output
