"""Secret token generation contract."""

from abc import ABC, abstractmethod


class GeradorDeTokenInterface(ABC):

    @abstractmethod
    def gerar(self) -> str:
        """Return a new unpredictable, URL-safe token."""
