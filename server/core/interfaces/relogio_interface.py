"""Clock contract, so time-based rules can be tested without sleeping."""

from abc import ABC, abstractmethod
from datetime import datetime


class RelogioInterface(ABC):

    @abstractmethod
    def agora(self) -> datetime:
        """Return the current time as a timezone-aware UTC datetime."""
