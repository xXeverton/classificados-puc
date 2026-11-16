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
    ) -> tuple[list[Ad], int]:
        """Return one page of available advertisements and the total count."""
