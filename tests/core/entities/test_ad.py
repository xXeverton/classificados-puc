from datetime import datetime, timezone

import pytest

from server.core.entities.ad import Ad


def valid_ad_data():
    return {
        "title": "Bicicleta usada",
        "description": "Bicicleta em bom estado.",
        "type": "product",
        "category": "Esportes",
        "price": 450.0,
        "image_url": None,
        "created_at": datetime(2026, 11, 12, 10, 0, tzinfo=timezone.utc),
        "status": "published",
    }


def test_ad_accepts_published_ad_without_photo():
    ad = Ad(**valid_ad_data())

    assert ad.title == "Bicicleta usada"
    assert ad.image_url is None
    assert ad.status == "published"


@pytest.mark.parametrize(
    "status",
    ["published", "sold", "expired"],
)
def test_ad_accepts_supported_statuses(status):
    data = valid_ad_data()
    data["status"] = status

    ad = Ad(**data)

    assert ad.status == status


@pytest.mark.parametrize(
    "required_field",
    ["title", "type", "category", "price", "created_at", "status"],
)
def test_ad_rejects_missing_required_field(required_field):
    data = valid_ad_data()
    data.pop(required_field)

    with pytest.raises(TypeError):
        Ad(**data)
