"""Repository contract consumed by advertisement-related use cases."""

from abc import ABC, abstractmethod

from server.core.entities.ad import Ad


class AdRepository(ABC):
    """Persistence operations required to list published advertisements."""

    @abstractmethod
    def list_published(
        self,
        page: int,
        per_page: int,
        search: str | None,
        ad_type: str | None,
        category: str | None = None,
        min_price: float | None = None,
        max_price: float | None = None,
    ) -> tuple[list[Ad], int]:
        """Return one page of available advertisements and the total count.

        `category` matches the whole name ignoring case; the price limits
        are inclusive. `None` means the filter is not applied.
        """
