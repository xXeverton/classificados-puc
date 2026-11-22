from datetime import UTC, datetime

import pytest
from sqlalchemy import select
from werkzeug.security import check_password_hash

from server.api.demo_data import (
    DEMO_AD_TITLES,
    DEMO_EMAIL,
    DEMO_USERNAME,
    create_demo_data,
)
from server.app import create_app
from server.infra.db.models import AdModel, AnuncianteModel, UsuarioModel

AGORA = datetime(2026, 11, 22, 12, 0, tzinfo=UTC)


def create_memory_app():
    return create_app(
        {
            "DATABASE_URL": "sqlite:///:memory:",
            "CORS_ORIGINS": [],
        }
    )


def test_demo_seed_creates_login_profile_and_sample_ads_idempotently():
    app = create_memory_app()
    session_factory = app.extensions["session_factory"]

    created = create_demo_data(session_factory, "senha-demo-segura", AGORA)
    created_again = create_demo_data(
        session_factory, "nova-senha-demo-segura", AGORA
    )

    with session_factory() as session:
        user = session.scalar(
            select(UsuarioModel).where(UsuarioModel.email == DEMO_EMAIL)
        )
        ads = session.scalars(
            select(AdModel).where(AdModel.usuario_id == user.id)
        ).all()
        advertiser = session.scalar(
            select(AnuncianteModel).where(
                AnuncianteModel.usuario_id == user.id
            )
        )

        assert user.nome_usuario == DEMO_USERNAME
        assert user.confirmado_em is not None
        assert check_password_hash(
            user.senha_hash, "nova-senha-demo-segura"
        )
        assert advertiser is not None
        assert {ad.title for ad in ads} == set(DEMO_AD_TITLES)
        assert {
            status: sum(ad.status == status for ad in ads)
            for status in ("published", "expired", "sold")
        } == {"published": 4, "expired": 3, "sold": 1}

    assert created == 8
    assert created_again == 0
    app.extensions["database_engine"].dispose()


def test_demo_seed_backfills_added_ads_for_existing_demo_user():
    app = create_memory_app()
    session_factory = app.extensions["session_factory"]
    create_demo_data(session_factory, "senha-demo-segura", AGORA)

    with session_factory.begin() as session:
        session.query(AdModel).filter(
            AdModel.title.in_(DEMO_AD_TITLES[3:])
        ).delete(synchronize_session=False)

    created = create_demo_data(session_factory, "senha-demo-segura", AGORA)

    with session_factory() as session:
        ads = session.scalars(select(AdModel)).all()
        assert {ad.title for ad in ads} == set(DEMO_AD_TITLES)

    assert created == len(DEMO_AD_TITLES) - 3
    app.extensions["database_engine"].dispose()


def test_demo_seed_refuses_reserved_identifiers_owned_by_another_user():
    app = create_memory_app()
    session_factory = app.extensions["session_factory"]
    with session_factory.begin() as session:
        session.add(
            UsuarioModel(
                nome="Outra pessoa",
                email=DEMO_EMAIL,
                nome_usuario="outro-usuario",
                matricula=None,
                vinculo="aluno",
                senha_hash="hash-existente",
                confirmado_em=AGORA,
            )
        )

    with pytest.raises(ValueError, match="já estão em uso"):
        create_demo_data(session_factory, "senha-demo-segura", AGORA)

    with session_factory() as session:
        user = session.scalar(
            select(UsuarioModel).where(UsuarioModel.email == DEMO_EMAIL)
        )
        assert user.nome_usuario == "outro-usuario"
        assert user.senha_hash == "hash-existente"
    app.extensions["database_engine"].dispose()


def test_demo_command_requires_explicit_opt_in(monkeypatch):
    app = create_memory_app()
    monkeypatch.delenv("ALLOW_DEMO_DATA", raising=False)
    monkeypatch.setenv("DEMO_PASSWORD", "senha-demo-segura")

    result = app.test_cli_runner().invoke(args=["criar-dados-demo"])

    assert result.exit_code != 0
    assert "ALLOW_DEMO_DATA=1" in result.output
    app.extensions["database_engine"].dispose()


def test_demo_command_refuses_non_default_database(monkeypatch):
    app = create_memory_app()
    monkeypatch.setenv("ALLOW_DEMO_DATA", "1")
    monkeypatch.setenv("DEMO_PASSWORD", "senha-demo-segura")

    result = app.test_cli_runner().invoke(args=["criar-dados-demo"])

    assert result.exit_code != 0
    assert "SQLite local padrão" in result.output
    app.extensions["database_engine"].dispose()
