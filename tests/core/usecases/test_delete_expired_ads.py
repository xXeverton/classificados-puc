from datetime import UTC, datetime, timedelta

from server.core.entities.ad import Ad
from server.core.interfaces.deletable_ad_repository_interface import (
    DeletableAdRepository,
)
from server.core.usecases.delete_expired_ads import DeleteExpiredAds
from tests.core.usecases.fakes import RelogioFalso

NOW = datetime(2027, 3, 1, 12, 0, tzinfo=UTC)


class InMemoryDeletableAdRepository(DeletableAdRepository):
    def __init__(self, ads, image_keys=None):
        self.ads = {ad.id: ad for ad in ads}
        self.image_keys = image_keys or {}

    def list_expired_ads(self):
        return [ad for ad in self.ads.values() if ad.status == "expired"]

    def delete_expired(self, ad_ids):
        keys = []
        for ad_id in ad_ids:
            ad = self.ads.get(ad_id)
            if ad is not None and ad.status == "expired":
                del self.ads[ad_id]
                keys.append(self.image_keys.get(ad_id))
        return keys


def make_ad(ad_id, ended_days_ago, status="expired"):
    end = NOW - timedelta(days=ended_days_ago)
    return Ad(
        id=ad_id,
        title=f"Anúncio {ad_id}",
        type="product",
        category="produto",
        price=10.0,
        created_at=end - timedelta(days=30),
        status=status,
        expires_at=end,
    )


def run(ads, image_keys=None):
    repository = InMemoryDeletableAdRepository(ads, image_keys)
    result = DeleteExpiredAds(repository, RelogioFalso(NOW)).execute()
    return repository, result


def test_deletes_ads_expired_thirty_days_ago_or_more_with_their_photos():
    repository, result = run(
        [make_ad(1, 30), make_ad(2, 45), make_ad(3, 29)],
        image_keys={1: "anuncios/um.webp"},
    )

    assert sorted(repository.ads) == [3]
    assert result.deleted == 2
    assert sorted(result.image_keys) == ["anuncios/um.webp"]


def test_keeps_published_and_sold_ads_whatever_their_age():
    repository, result = run(
        [make_ad(1, 90, status="published"), make_ad(2, 90, status="sold")]
    )

    assert sorted(repository.ads) == [1, 2]
    assert result.deleted == 0
    assert result.image_keys == []


def test_second_run_deletes_nothing():
    repository = InMemoryDeletableAdRepository([make_ad(1, 40)])
    delete = DeleteExpiredAds(repository, RelogioFalso(NOW))

    assert delete.execute().deleted == 1
    assert delete.execute().deleted == 0


def test_does_nothing_without_ads():
    _, result = run([])

    assert result.deleted == 0
    assert result.image_keys == []
