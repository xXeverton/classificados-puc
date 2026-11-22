"""Repository contract consumed by the edit and delete ad use cases."""

from abc import ABC, abstractmethod

from server.core.entities.ad import Ad
from server.core.entities.anuncio import Anuncio


class AnuncioEditavelRepositoryInterface(ABC):
    """Persistence operations an owner needs to manage an advertisement."""

    @abstractmethod
    def buscar_por_id(self, ad_id: int) -> Ad | None:
        """Return the advertisement in any status, or None if missing."""

    @abstractmethod
    def atualizar(self, ad_id: int, anuncio: Anuncio) -> Ad:
        """Replace the editable fields and return the updated ad.

        Title, description, price, "a combinar" and condition change;
        dates, status, owner and photo are kept.
        """

    @abstractmethod
    def excluir(self, ad_id: int) -> None:
        """Delete the advertisement permanently."""
