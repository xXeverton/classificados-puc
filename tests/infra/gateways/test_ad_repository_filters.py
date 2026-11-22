"""Category and price filters of the advertisement repository."""

from datetime import datetime, timezone

from server.infra.db.database import create_session_factory
from server.infra.gateways.ad_repository_sqlalchemy import (
    AdRepositorySQLAlchemy,
)
from tests.infra.gateways.test_ad_repository_sqlalchemy import (
    add_ads,
    make_ad_model,
)


def make_priced_ad_model(title, price, category="Esportes", **options):
    model = make_ad_model(
        title,
        datetime(2026, 11, 10, tzinfo=timezone.utc),
        category=category,
        **options,
    )
    model.price = price
    return model


def list_titles(database_engine, **filters):
    repository = AdRepositorySQLAlchemy(
        create_session_factory(database_engine),
    )
    filters.setdefault("search", None)
    filters.setdefault("ad_type", None)
    items, total = repository.list_published(page=1, per_page=20, **filters)
    return sorted(ad.title for ad in items), total


def test_repository_filters_by_category_ignoring_case(database_engine):
    add_ads(
        database_engine,
        [
            make_priced_ad_model("Notebook", 900, category="Eletrônicos"),
            make_priced_ad_model("Bicicleta", 450, category="Esportes"),
        ],
    )

    assert list_titles(database_engine, category="ELETRÔNICOS") == (
        ["Notebook"],
        1,
    )


def test_repository_filters_by_inclusive_price_range(database_engine):
    add_ads(
        database_engine,
        [
            make_priced_ad_model("Barato", 49.99),
            make_priced_ad_model("No mínimo", 50),
            make_priced_ad_model("No máximo", 100),
            make_priced_ad_model("Caro!", 100.01),
        ],
    )

    assert list_titles(database_engine, min_price=50, max_price=100) == (
        ["No máximo", "No mínimo"],
        2,
    )
    assert list_titles(database_engine, min_price=100)[0] == [
        "Caro!",
        "No máximo",
    ]
    assert list_titles(database_engine, max_price=50)[0] == [
        "Barato",
        "No mínimo",
    ]


def test_repository_combines_category_price_search_and_type(
    database_engine,
):
    add_ads(
        database_engine,
        [
            make_priced_ad_model("Notebook gamer", 3000,
                                 category="Eletrônicos"),
            make_priced_ad_model("Notebook simples", 900,
                                 category="Eletrônicos"),
            make_priced_ad_model("Notebook de papel", 20,
                                 category="Papelaria"),
            make_priced_ad_model(
                "Conserto de notebook",
                150,
                category="Eletrônicos",
                ad_type="service",
            ),
            make_priced_ad_model(
                "Notebook vendido",
                500,
                category="Eletrônicos",
                status="sold",
            ),
        ],
    )

    assert list_titles(
        database_engine,
        search="notebook",
        ad_type="product",
        category="eletrônicos",
        max_price=1000,
    ) == (["Notebook simples"], 1)
