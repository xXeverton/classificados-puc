"""Repository contract consumed by the featured events use case."""

from abc import ABC, abstractmethod
from datetime import date

from server.core.entities.ad import Ad


class EventosEmDestaqueRepository(ABC):
    """Read-only access to the upcoming published events."""

    @abstractmethod
    def listar_eventos_futuros(
        self, a_partir_de: date, limite: int
    ) -> list[Ad]:
        """Return published events on or after `a_partir_de`.

        Ordered by event day, then by publication time, then by id, and
        cut to `limite` items.
        """
