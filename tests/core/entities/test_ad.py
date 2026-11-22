from datetime import datetime, timedelta, timezone

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


PUBLISHED_AT = datetime(2026, 11, 1, 10, 0, tzinfo=timezone.utc)


def ad_with(status="published", expires_at=None):
    data = valid_ad_data()
    data.update(
        status=status, created_at=PUBLISHED_AT, expires_at=expires_at
    )
    return Ad(**data)


def test_publication_period_is_thirty_days():
    assert Ad.PUBLICATION_PERIOD == timedelta(days=30)


def test_publication_ends_thirty_days_after_creation_without_end_date():
    ad = ad_with()

    assert ad.publication_ends_at() == PUBLISHED_AT + timedelta(days=30)


def test_publication_ends_at_registered_end_date():
    renewed_until = PUBLISHED_AT + timedelta(days=45)
    ad = ad_with(expires_at=renewed_until)

    assert ad.publication_ends_at() == renewed_until


def test_published_ad_is_not_overdue_before_the_end():
    ad = ad_with()
    end = ad.publication_ends_at()

    assert not ad.is_overdue(end - timedelta(seconds=1))


def test_published_ad_is_overdue_at_the_exact_end():
    ad = ad_with()

    assert ad.is_overdue(ad.publication_ends_at())


def test_renewed_ad_uses_new_end_instead_of_creation_date():
    ad = ad_with(expires_at=PUBLISHED_AT + timedelta(days=45))

    assert not ad.is_overdue(PUBLISHED_AT + timedelta(days=31))
    assert ad.is_overdue(PUBLISHED_AT + timedelta(days=45))


@pytest.mark.parametrize("status", ["sold", "expired"])
def test_ad_that_is_not_published_is_never_overdue(status):
    ad = ad_with(status=status)

    assert not ad.is_overdue(PUBLISHED_AT + timedelta(days=365))


def test_retention_after_expiry_is_thirty_days():
    assert Ad.RETENTION_AFTER_EXPIRY == timedelta(days=30)


def test_expired_ad_can_be_deleted_thirty_days_after_its_end():
    ad = ad_with(status="expired")
    end = ad.publication_ends_at()

    limit = end + timedelta(days=30)

    assert not ad.can_be_deleted(limit - timedelta(seconds=1))
    assert ad.can_be_deleted(limit)


def test_deletion_counts_from_renewed_end_date():
    renewed_until = PUBLISHED_AT + timedelta(days=50)
    ad = ad_with(status="expired", expires_at=renewed_until)

    assert not ad.can_be_deleted(PUBLISHED_AT + timedelta(days=79))
    assert ad.can_be_deleted(PUBLISHED_AT + timedelta(days=80))


@pytest.mark.parametrize("status", ["published", "sold"])
def test_ad_that_is_not_expired_is_never_deleted(status):
    ad = ad_with(status=status)

    assert not ad.can_be_deleted(PUBLISHED_AT + timedelta(days=365))
