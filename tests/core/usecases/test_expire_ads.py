from dataclasses import replace
from datetime import UTC, datetime, timedelta

from server.core.entities.ad import Ad
from server.core.interfaces.expirable_ad_repository_interface import (
    ExpirableAdRepository,
)
from server.core.usecases.expire_ads import ExpireAds
from tests.core.usecases.fakes import RelogioFalso

NOW = datetime(2026, 12, 15, 12, 0, tzinfo=UTC)


class InMemoryExpirableAdRepository(ExpirableAdRepository):
    def __init__(self, ads):
        self.ads = {ad.id: ad for ad in ads}

    def list_published_ads(self):
        return [ad for ad in self.ads.values() if ad.status == "published"]

    def mark_as_expired(self, ad_ids):
        changed = 0
        for ad_id in ad_ids:
            ad = self.ads[ad_id]
            if ad.status == "published":
                self.ads[ad_id] = replace(ad, status="expired")
                changed += 1
        return changed

    def status_of(self, ad_id):
        return self.ads[ad_id].status


def make_ad(ad_id, created_at, status="published", expires_at=None):
    return Ad(
        id=ad_id,
        title=f"Anúncio {ad_id}",
        type="product",
        category="Livros",
        price=10.0,
        created_at=created_at,
        status=status,
        expires_at=expires_at,
    )


def expire(ads, now=NOW):
    repository = InMemoryExpirableAdRepository(ads)
    expired = ExpireAds(repository, RelogioFalso(now)).execute()
    return repository, expired


def test_expires_published_ad_past_thirty_days():
    repository, expired = expire([make_ad(1, NOW - timedelta(days=31))])

    assert repository.status_of(1) == "expired"
    assert expired == 1


def test_keeps_published_ad_within_thirty_days():
    repository, expired = expire([make_ad(1, NOW - timedelta(days=29))])

    assert repository.status_of(1) == "published"
    assert expired == 0


def test_expires_ad_exactly_when_period_ends():
    repository, expired = expire([make_ad(1, NOW - timedelta(days=30))])

    assert repository.status_of(1) == "expired"
    assert expired == 1


def test_renewed_ad_follows_its_new_end_date():
    old_but_renewed = make_ad(
        1,
        NOW - timedelta(days=40),
        expires_at=NOW + timedelta(days=5),
    )
    renewal_ended = make_ad(
        2,
        NOW - timedelta(days=10),
        expires_at=NOW - timedelta(minutes=1),
    )

    repository, expired = expire([old_but_renewed, renewal_ended])

    assert repository.status_of(1) == "published"
    assert repository.status_of(2) == "expired"
    assert expired == 1


def test_does_not_change_sold_or_already_expired_ads():
    repository, expired = expire(
        [
            make_ad(1, NOW - timedelta(days=60), status="sold"),
            make_ad(2, NOW - timedelta(days=60), status="expired"),
        ]
    )

    assert repository.status_of(1) == "sold"
    assert repository.status_of(2) == "expired"
    assert expired == 0


def test_second_run_without_new_overdue_ads_expires_nothing():
    repository = InMemoryExpirableAdRepository(
        [make_ad(1, NOW - timedelta(days=31))]
    )
    expire_ads = ExpireAds(repository, RelogioFalso(NOW))

    assert expire_ads.execute() == 1
    assert expire_ads.execute() == 0
    assert repository.status_of(1) == "expired"


def test_reports_how_many_ads_expired():
    _, expired = expire(
        [
            make_ad(1, NOW - timedelta(days=31)),
            make_ad(2, NOW - timedelta(days=45)),
            make_ad(3, NOW - timedelta(days=2)),
        ]
    )

    assert expired == 2


def test_does_nothing_when_there_are_no_ads():
    _, expired = expire([])

    assert expired == 0
