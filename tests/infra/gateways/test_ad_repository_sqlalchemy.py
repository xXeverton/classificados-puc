from datetime import datetime, timedelta, timezone

import pytest

from server.infra.db.database import create_session_factory
from server.infra.db.models import AdModel
from server.infra.gateways.ad_repository_sqlalchemy import (
    AdRepositorySQLAlchemy,
)


def add_ads(database_engine, ads):
    session_factory = create_session_factory(database_engine)
    with session_factory.begin() as session:
        session.add_all(ads)


def make_ad_model(
    title,
    created_at,
    status="published",
    ad_type="product",
    description="Descrição do anúncio.",
    category="Esportes",
    expires_at=None,
):
    return AdModel(
        title=title,
        description=description,
        type=ad_type,
        category=category,
        price=100.0,
        image_url=None,
        created_at=created_at,
        status=status,
        expires_at=expires_at,
    )


def test_repository_lists_only_available_ads_in_descending_order(
    database_engine,
):
    older_ad = make_ad_model(
        "Anúncio antigo",
        datetime(2026, 11, 10, tzinfo=timezone.utc),
    )
    newer_ad = make_ad_model(
        "Anúncio recente",
        datetime(2026, 11, 12, tzinfo=timezone.utc),
    )
    sold_ad = make_ad_model(
        "Anúncio vendido",
        datetime(2026, 11, 13, tzinfo=timezone.utc),
        status="sold",
    )
    expired_ad = make_ad_model(
        "Anúncio expirado",
        datetime(2026, 11, 14, tzinfo=timezone.utc),
        status="expired",
    )
    add_ads(
        database_engine,
        [older_ad, newer_ad, sold_ad, expired_ad],
    )
    repository = AdRepositorySQLAlchemy(
        create_session_factory(database_engine),
    )

    items, total = repository.list_published(
        page=1,
        per_page=20,
        search=None,
        ad_type=None,
    )

    assert [ad.title for ad in items] == [
        "Anúncio recente",
        "Anúncio antigo",
    ]
    assert total == 2


@pytest.mark.parametrize(
    ("search", "expected_title"),
    [
        ("BICICLETA", "Bicicleta urbana"),
        ("UNIVERSIDADE", "Cadeira de estudo"),
        ("ESPORTES", "Livro de esportes"),
    ],
)
def test_repository_searches_title_description_and_category(
    database_engine,
    search,
    expected_title,
):
    add_ads(
        database_engine,
        [
            make_ad_model(
                "Bicicleta urbana",
                datetime(2026, 11, 12, tzinfo=timezone.utc),
                category="Veículos",
            ),
            make_ad_model(
                "Cadeira de estudo",
                datetime(2026, 11, 11, tzinfo=timezone.utc),
                description="Cadeira para estudar na universidade.",
                category="Móveis",
            ),
            make_ad_model(
                "Livro de esportes",
                datetime(2026, 11, 10, tzinfo=timezone.utc),
                description="Livro usado em bom estado.",
                category="Livros",
            ),
        ],
    )
    repository = AdRepositorySQLAlchemy(
        create_session_factory(database_engine),
    )

    items, total = repository.list_published(
        page=1,
        per_page=20,
        search=search,
        ad_type=None,
    )

    assert [ad.title for ad in items] == [expected_title]
    assert total == 1


def test_repository_filters_by_ad_type(database_engine):
    add_ads(
        database_engine,
        [
            make_ad_model(
                "Notebook",
                datetime(2026, 11, 12, tzinfo=timezone.utc),
                ad_type="product",
            ),
            make_ad_model(
                "Aulas de inglês",
                datetime(2026, 11, 11, tzinfo=timezone.utc),
                ad_type="service",
            ),
        ],
    )
    repository = AdRepositorySQLAlchemy(
        create_session_factory(database_engine),
    )

    items, total = repository.list_published(
        page=1,
        per_page=20,
        search=None,
        ad_type="service",
    )

    assert [ad.title for ad in items] == ["Aulas de inglês"]
    assert total == 1


def test_repository_applies_limit_offset_and_returns_total(
    database_engine,
):
    ads = [
        make_ad_model(
            f"Anúncio {index:02d}",
            datetime(2026, 11, 1, tzinfo=timezone.utc)
            + timedelta(days=index),
        )
        for index in range(25)
    ]
    add_ads(database_engine, ads)
    repository = AdRepositorySQLAlchemy(
        create_session_factory(database_engine),
    )

    items, total = repository.list_published(
        page=2,
        per_page=20,
        search=None,
        ad_type=None,
    )

    assert [ad.title for ad in items] == [
        f"Anúncio {index:02d}" for index in range(4, -1, -1)
    ]
    assert len(items) == 5
    assert total == 25


def make_repository(database_engine):
    return AdRepositorySQLAlchemy(create_session_factory(database_engine))


def ads_by_title(database_engine):
    session_factory = create_session_factory(database_engine)
    with session_factory() as session:
        return {
            model.title: (model.id, model.status)
            for model in session.query(AdModel).all()
        }


def test_repository_lists_every_published_ad_with_its_end_date(
    database_engine,
):
    renewed_until = datetime(2026, 12, 30, tzinfo=timezone.utc)
    add_ads(
        database_engine,
        [
            make_ad_model(
                "Publicado",
                datetime(2026, 11, 1, tzinfo=timezone.utc),
                expires_at=renewed_until,
            ),
            make_ad_model(
                "Vendido",
                datetime(2026, 11, 2, tzinfo=timezone.utc),
                status="sold",
            ),
            make_ad_model(
                "Expirado",
                datetime(2026, 11, 3, tzinfo=timezone.utc),
                status="expired",
            ),
        ],
    )

    ads = make_repository(database_engine).list_published_ads()

    assert [ad.title for ad in ads] == ["Publicado"]
    assert ads[0].expires_at == renewed_until


def test_repository_marks_only_published_ads_as_expired(database_engine):
    created_at = datetime(2026, 11, 1, tzinfo=timezone.utc)
    add_ads(
        database_engine,
        [
            make_ad_model("Vencido", created_at),
            make_ad_model("Em dia", created_at),
            make_ad_model("Vendido", created_at, status="sold"),
        ],
    )
    ids = {title: ad_id for title, (ad_id, _) in
           ads_by_title(database_engine).items()}

    changed = make_repository(database_engine).mark_as_expired(
        [ids["Vencido"], ids["Vendido"]]
    )

    assert changed == 1
    statuses = {
        title: status
        for title, (_, status) in ads_by_title(database_engine).items()
    }
    assert statuses == {
        "Vencido": "expired",
        "Em dia": "published",
        "Vendido": "sold",
    }


def test_repository_marks_nothing_for_empty_list(database_engine):
    add_ads(
        database_engine,
        [make_ad_model("Em dia", datetime(2026, 11, 1, tzinfo=timezone.utc))],
    )

    changed = make_repository(database_engine).mark_as_expired([])

    assert changed == 0
    assert ads_by_title(database_engine)["Em dia"][1] == "published"
