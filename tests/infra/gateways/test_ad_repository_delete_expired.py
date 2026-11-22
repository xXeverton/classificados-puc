"""Listing and deleting expired ads in the advertisement repository."""

from datetime import UTC, datetime

from server.infra.db.database import create_session_factory
from server.infra.db.models import AdModel
from server.infra.gateways.deletable_ad_repository_sqlalchemy import (
    DeletableAdRepositorySQLAlchemy,
)
from tests.infra.gateways.test_ad_repository_sqlalchemy import (
    add_ads,
    make_ad_model,
)

CREATED_AT = datetime(2026, 9, 1, tzinfo=UTC)


def model(title, status, image_key=None):
    ad = make_ad_model(title, CREATED_AT, status=status)
    ad.image_key = image_key
    return ad


def repository_and_ids(database_engine, ads):
    add_ads(database_engine, ads)
    session_factory = create_session_factory(database_engine)
    with session_factory() as session:
        ids = {ad.title: ad.id for ad in session.query(AdModel).all()}
    return (
        DeletableAdRepositorySQLAlchemy(session_factory),
        session_factory,
        ids,
    )


def test_lists_only_expired_ads(database_engine):
    repository, _, _ = repository_and_ids(
        database_engine,
        [
            model("Expirado", "expired"),
            model("Publicado", "published"),
            model("Vendido", "sold"),
        ],
    )

    assert [ad.title for ad in repository.list_expired_ads()] == ["Expirado"]


def test_deletes_only_ads_still_expired_and_returns_photo_keys(
    database_engine,
):
    repository, session_factory, ids = repository_and_ids(
        database_engine,
        [
            model("Com foto", "expired", image_key="anuncios/foto.webp"),
            model("Sem foto", "expired"),
            model("Renovado no meio tempo", "published"),
        ],
    )

    keys = repository.delete_expired(
        [ids["Com foto"], ids["Sem foto"], ids["Renovado no meio tempo"]]
    )

    assert sorted(keys, key=lambda key: key or "") == [
        None,
        "anuncios/foto.webp",
    ]
    with session_factory() as session:
        titles = [ad.title for ad in session.query(AdModel).all()]
    assert titles == ["Renovado no meio tempo"]


def test_deletes_nothing_for_empty_list(database_engine):
    repository, session_factory, _ = repository_and_ids(
        database_engine, [model("Expirado", "expired")]
    )

    assert repository.delete_expired([]) == []
    with session_factory() as session:
        assert session.query(AdModel).count() == 1
