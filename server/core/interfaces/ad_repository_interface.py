"""Repository contract consumed by advertisement-related use cases."""

from abc import ABC, abstractmethod
from datetime import datetime

from server.core.entities.anuncio import Anuncio
from server.core.entities.ad import Ad


class AdRepository(ABC):
    """Persistence operations required to list published advertisements."""

    @abstractmethod
    def buscar_por_id(self, anuncio_id: int) -> Ad | None:
        """Return an ad by ID, including unavailable states."""

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

    @abstractmethod
    def publish(
        self,
        anuncio: Anuncio,
        nome_anunciante: str,
        criado_em: datetime,
        expira_em: datetime,
    ) -> Ad:
        """Persist a validated announcement and return its feed item."""
