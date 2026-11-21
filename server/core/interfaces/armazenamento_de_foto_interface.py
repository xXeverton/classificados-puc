"""Storage contract for profile photos."""

from abc import ABC, abstractmethod

from server.core.entities.foto_de_perfil import FotoDePerfil


class ArmazenamentoDeFotoInterface(ABC):

    @abstractmethod
    def salvar(self, foto: FotoDePerfil) -> str:
        """Store the photo and return its ``foto_url``."""

    @abstractmethod
    def ler(self, foto_url: str) -> bytes | None:
        """Return the stored bytes, or None when there is no such photo."""

    @abstractmethod
    def remover(self, foto_url: str) -> None:
        """Delete the photo; a missing photo is not an error."""
