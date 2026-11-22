"""Repository contract consumed by the ad expiration use case."""

from abc import ABC, abstractmethod

from server.core.entities.ad import Ad


class ExpirableAdRepository(ABC):
    """Persistence operations required to expire overdue advertisements."""

    @abstractmethod
    def list_published_ads(self) -> list[Ad]:
        """Return every advertisement that is currently published."""

    @abstractmethod
    def mark_as_expired(self, ad_ids: list[int]) -> int:
        """Expire the given ads that are still published.

        Returns how many ads changed. Ads that are no longer published,
        such as one sold in the meantime, are left untouched.
        """
