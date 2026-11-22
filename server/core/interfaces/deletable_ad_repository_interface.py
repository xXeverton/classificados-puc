"""Repository contract consumed by the expired ad deletion use case."""

from abc import ABC, abstractmethod

from server.core.entities.ad import Ad


class DeletableAdRepository(ABC):
    """Persistence operations required to delete old expired ads."""

    @abstractmethod
    def list_expired_ads(self) -> list[Ad]:
        """Return every advertisement that is currently expired."""

    @abstractmethod
    def delete_expired(self, ad_ids: list[int]) -> list[str | None]:
        """Delete the given ads that are still expired.

        Returns the photo key of each deleted ad (None when it has no
        photo). Ads renewed in the meantime are left untouched.
        """
