"""Repository contract consumed by advertisement-related use cases."""

from abc import ABC, abstractmethod
from datetime import datetime

from server.core.entities.anuncio import Anuncio
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

    @abstractmethod
    def publish(
        self,
        anuncio: Anuncio,
        nome_anunciante: str,
        criado_em: datetime,
        expira_em: datetime,
    ) -> Ad:
        """Persist a validated announcement and return its feed item."""
