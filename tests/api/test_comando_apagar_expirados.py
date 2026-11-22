"""Command `apagar-anuncios-expirados` (spec 008, PROJ-41)."""

from datetime import UTC, datetime, timedelta
from io import BytesIO

from server.app import create_app
from server.infra.db.models import AdModel
from server.infra.storage.storage import StorageIndisponivelError
from tests.core.usecases.fakes import RelogioFalso

NOW = datetime(2027, 3, 1, 12, 0, tzinfo=UTC)
PNG = b"\x89PNG\r\n\x1a\nconteudo"


def ad_model(title, status, ended_days_ago, image_key=None):
    end = NOW - timedelta(days=ended_days_ago)
    return AdModel(
        title=title,
        description="Anúncio de teste.",
        type="product",
        category="produto",
        price=10.0,
        image_url=None,
        created_at=end - timedelta(days=30),
        status=status,
        expires_at=end,
        image_key=image_key,
    )


def create_app_with_storage(tmp_path):
    return create_app(
        {
            "DATABASE_URL": "sqlite:///:memory:",
            "CORS_ORIGINS": [],
            "RELOGIO": RelogioFalso(NOW),
            "STORAGE_LOCAL_ROOT": str(tmp_path / "media"),
        }
    )


def stored_files(tmp_path):
    return [path for path in (tmp_path / "media").rglob("*") if path.is_file()]


def titles_in_database(app):
    with app.extensions["session_factory"]() as session:
        return sorted(ad.title for ad in session.query(AdModel).all())


def test_command_deletes_old_expired_ads_and_their_photos(tmp_path):
    app = create_app_with_storage(tmp_path)
    key = app.extensions["image_storage"].salvar_imagem(
        BytesIO(PNG), namespace="anuncios"
    ).chave
    with app.extensions["session_factory"].begin() as session:
        session.add_all(
            [
                ad_model("Expirado antigo", "expired", 31, image_key=key),
                ad_model("Expirado recente", "expired", 10),
                ad_model("Publicado antigo", "published", 90),
                ad_model("Vendido antigo", "sold", 90),
            ]
        )
    assert len(stored_files(tmp_path)) == 1

    result = app.test_cli_runner().invoke(args=["apagar-anuncios-expirados"])

    assert result.exit_code == 0
    assert "1 anúncio(s) apagado(s)." in result.output
    assert titles_in_database(app) == [
        "Expirado recente",
        "Publicado antigo",
        "Vendido antigo",
    ]
    assert stored_files(tmp_path) == []
    app.extensions["database_engine"].dispose()


def test_command_reports_zero_when_nothing_is_old_enough(tmp_path):
    app = create_app_with_storage(tmp_path)
    with app.extensions["session_factory"].begin() as session:
        session.add(ad_model("Expirado recente", "expired", 5))

    result = app.test_cli_runner().invoke(args=["apagar-anuncios-expirados"])

    assert result.exit_code == 0
    assert "0 anúncio(s) apagado(s)." in result.output
    assert titles_in_database(app) == ["Expirado recente"]
    app.extensions["database_engine"].dispose()


def test_command_keeps_deletion_when_photo_cannot_be_removed(
    tmp_path, monkeypatch
):
    app = create_app_with_storage(tmp_path)
    storage = app.extensions["image_storage"]
    key = storage.salvar_imagem(BytesIO(PNG), namespace="anuncios").chave
    with app.extensions["session_factory"].begin() as session:
        session.add(ad_model("Expirado antigo", "expired", 40, image_key=key))

    def storage_down(chave):
        raise StorageIndisponivelError("Armazenamento fora do ar.")

    monkeypatch.setattr(storage, "remover", storage_down)

    result = app.test_cli_runner().invoke(args=["apagar-anuncios-expirados"])

    assert result.exit_code == 0
    assert "1 anúncio(s) apagado(s)." in result.output
    assert "1 foto(s) não puderam ser apagadas" in result.output
    assert titles_in_database(app) == []
    app.extensions["database_engine"].dispose()
