from datetime import datetime, timedelta, timezone

import pytest

from server.core.entities.ad import Ad
from server.core.entities.usuario import Usuario
from server.core.interfaces.ad_repository_interface import AdRepository
from server.core.usecases.erros import ErroDeCasoDeUso
from server.core.usecases.list_ads import ListAds


class InMemoryAdRepository(AdRepository):
    def __init__(self, ads):
        self.ads = ads
        self.calls = []

    def list_published(self, page, per_page, search, ad_type):
        self.calls.append((page, per_page, search, ad_type))
        available_ads = [
            ad for ad in self.ads if ad.status == "published"
        ]
        if ad_type not in (None, "all"):
            available_ads = [
                ad for ad in available_ads if ad.type == ad_type
            ]
        if search is not None:
            search_term = search.lower()
            available_ads = [
                ad
                for ad in available_ads
                if search_term in " ".join(
                    [
                        ad.title,
                        ad.description or "",
                        ad.category,
                    ],
                ).lower()
            ]
        available_ads.sort(
            key=lambda ad: ad.created_at,
            reverse=True,
        )
        start = (page - 1) * per_page
        end = start + per_page
        return available_ads[start:end], len(available_ads)


def make_ad(
    title,
    status,
    description="Descrição do anúncio.",
    category="Esportes",
    ad_type="product",
    created_at=None,
):
    if created_at is None:
        created_at = datetime(
            2026,
            11,
            12,
            10,
            0,
            tzinfo=timezone.utc,
        )
    return Ad(
        title=title,
        description=description,
        type=ad_type,
        category=category,
        price=100.0,
        image_url=None,
        created_at=created_at,
        status=status,
    )


def make_authenticated_user():
    return Usuario(
        nome="Ana",
        email="ana@aluno.puc-rio.br",
        nome_usuario="ana123",
        matricula="123",
        vinculo="aluno",
        senha_hash="hash-de-teste",
    )


def test_list_ads_returns_published_ads_for_authenticated_user():
    published_ad = make_ad("Bicicleta publicada", "published")
    sold_ad = make_ad("Bicicleta vendida", "sold")
    repository = InMemoryAdRepository([published_ad, sold_ad])
    list_ads = ListAds(repository)

    result = list_ads.execute(usuario=make_authenticated_user())

    assert result["items"] == [published_ad]
    assert result["page"] == 1
    assert result["per_page"] == 20
    assert result["total_items"] == 1


@pytest.mark.parametrize(
    ("search", "expected_title"),
    [
        ("BICICLETA", "Bicicleta urbana"),
        ("UNIVERSIDADE", "Cadeira de estudo"),
        ("ESPORTES", "Livro de esportes"),
    ],
)
def test_list_ads_searches_title_description_and_category(
    search,
    expected_title,
):
    ads = [
        make_ad(
            "Bicicleta urbana",
            "published",
            category="Veículos",
        ),
        make_ad(
            "Cadeira de estudo",
            "published",
            description="Cadeira confortável para estudar na universidade.",
            category="Móveis",
        ),
        make_ad(
            "Livro de esportes",
            "published",
            description="Livro usado em bom estado.",
            category="Livros",
        ),
        make_ad("Mesa", "published", category="Casa"),
    ]
    repository = InMemoryAdRepository(ads)
    list_ads = ListAds(repository)

    result = list_ads.execute(
        usuario=make_authenticated_user(),
        search=search,
    )

    assert [ad.title for ad in result["items"]] == [expected_title]
    assert repository.calls == [(1, 20, search, None)]


@pytest.mark.parametrize(
    ("ad_type", "expected_titles"),
    [
        ("all", ["Notebook usado", "Aulas de inglês", "Mesa"]),
        ("product", ["Notebook usado", "Mesa"]),
        ("service", ["Aulas de inglês"]),
    ],
)
def test_list_ads_filters_all_products_and_services(
    ad_type,
    expected_titles,
):
    ads = [
        make_ad("Notebook usado", "published", ad_type="product"),
        make_ad(
            "Aulas de inglês",
            "published",
            category="Educação",
            ad_type="service",
        ),
        make_ad("Mesa", "published", category="Casa", ad_type="product"),
    ]
    repository = InMemoryAdRepository(ads)
    list_ads = ListAds(repository)

    result = list_ads.execute(
        usuario=make_authenticated_user(),
        ad_type=ad_type,
    )

    assert [ad.title for ad in result["items"]] == expected_titles
    assert repository.calls == [(1, 20, None, ad_type)]


def test_list_ads_combines_type_filter_with_search():
    ads = [
        make_ad("Notebook usado", "published", ad_type="product"),
        make_ad(
            "Curso de notebook",
            "published",
            category="Tecnologia",
            ad_type="service",
        ),
        make_ad(
            "Aulas de inglês",
            "published",
            category="Educação",
            ad_type="service",
        ),
    ]
    repository = InMemoryAdRepository(ads)
    list_ads = ListAds(repository)

    result = list_ads.execute(
        usuario=make_authenticated_user(),
        search="NOTEBOOK",
        ad_type="service",
    )

    assert [ad.title for ad in result["items"]] == ["Curso de notebook"]
    assert repository.calls == [(1, 20, "NOTEBOOK", "service")]


def test_list_ads_orders_by_creation_date_and_limits_page_to_20_items():
    ads = [
        make_ad(
            f"Anúncio {index:02d}",
            "published",
            created_at=datetime(
                2026,
                11,
                1,
                tzinfo=timezone.utc,
            ) + timedelta(days=index),
        )
        for index in range(25)
    ]
    repository = InMemoryAdRepository(ads)
    list_ads = ListAds(repository)

    result = list_ads.execute(
        usuario=make_authenticated_user(),
        page=1,
    )

    assert [ad.title for ad in result["items"]] == [
        f"Anúncio {index:02d}" for index in range(24, 4, -1)
    ]
    assert result["page"] == 1
    assert result["per_page"] == 20
    assert result["total_items"] == 25
    assert repository.calls == [(1, 20, None, None)]


def test_list_ads_returns_items_for_requested_page():
    ads = [
        make_ad(
            f"Anúncio {index:02d}",
            "published",
            created_at=datetime(
                2026,
                11,
                1,
                tzinfo=timezone.utc,
            ) + timedelta(days=index),
        )
        for index in range(25)
    ]
    repository = InMemoryAdRepository(ads)
    list_ads = ListAds(repository)

    result = list_ads.execute(
        usuario=make_authenticated_user(),
        page=2,
    )

    assert [ad.title for ad in result["items"]] == [
        f"Anúncio {index:02d}" for index in range(4, -1, -1)
    ]
    assert result["page"] == 2
    assert repository.calls == [(2, 20, None, None)]


def test_list_ads_returns_to_first_page_when_search_is_applied():
    ads = [
        make_ad(
            f"Anúncio {index:02d}",
            "published",
            created_at=datetime(
                2026,
                11,
                1,
                tzinfo=timezone.utc,
            ) + timedelta(days=index),
        )
        for index in range(25)
    ]
    repository = InMemoryAdRepository(ads)
    list_ads = ListAds(repository)

    result = list_ads.execute(
        usuario=make_authenticated_user(),
        page=2,
        search="Anúncio",
    )

    assert result["page"] == 1
    assert repository.calls == [(1, 20, "Anúncio", None)]


def test_list_ads_uses_first_page_when_page_is_not_provided():
    published_ad = make_ad("Bicicleta publicada", "published")
    repository = InMemoryAdRepository([published_ad])
    list_ads = ListAds(repository)

    result = list_ads.execute(usuario=make_authenticated_user())

    assert result["page"] == 1
    assert repository.calls == [(1, 20, None, None)]


def test_list_ads_returns_empty_feed_message_when_no_ads_are_available():
    repository = InMemoryAdRepository([])
    list_ads = ListAds(repository)

    result = list_ads.execute(usuario=make_authenticated_user())

    assert result == {
        "items": [],
        "page": 1,
        "per_page": 20,
        "total_pages": 0,
        "total_items": 0,
        "message": "Nenhum anúncio publicado encontrado.",
    }


@pytest.mark.parametrize(
    "invalid_arguments",
    [
        {"page": 0},
        {"page": -1},
        {"page": "1"},
        {"ad_type": "invalid"},
    ],
)
def test_list_ads_rejects_invalid_parameters(invalid_arguments):
    repository = InMemoryAdRepository([])
    list_ads = ListAds(repository)

    with pytest.raises(ValueError):
        list_ads.execute(
            usuario=make_authenticated_user(),
            **invalid_arguments,
        )


def test_list_ads_rejects_unauthenticated_user():
    repository = InMemoryAdRepository([])
    list_ads = ListAds(repository)

    with pytest.raises(ErroDeCasoDeUso):
        list_ads.execute(usuario=None)


def test_list_ads_excludes_sold_and_expired_ads():
    published_ad = make_ad("Bicicleta publicada", "published")
    sold_ad = make_ad("Bicicleta vendida", "sold")
    expired_ad = make_ad("Bicicleta expirada", "expired")
    repository = InMemoryAdRepository(
        [published_ad, sold_ad, expired_ad],
    )
    list_ads = ListAds(repository)

    result = list_ads.execute(usuario=make_authenticated_user())

    assert result["items"] == [published_ad]
    assert result["total_items"] == 1
