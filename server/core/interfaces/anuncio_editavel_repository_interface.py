"""Repository contract consumed by the edit and delete ad use cases."""

from abc import ABC, abstractmethod
from datetime import datetime

from server.core.entities.ad import Ad
from server.core.entities.anuncio import Anuncio


class AnuncioEditavelRepositoryInterface(ABC):
    """Persistence operations an owner needs to manage an advertisement."""

    @abstractmethod
    def buscar_por_id(self, ad_id: int) -> Ad | None:
        """Return the advertisement in any status, or None if missing."""

    @abstractmethod
    def atualizar(
        self,
        ad_id: int,
        anuncio: Anuncio,
        expires_at: datetime | None = None,
    ) -> Ad:
        """Replace the editable fields and return the updated ad.

        Title, description, price, "a combinar" and condition change;
        dates, status, owner and photo are kept unless a new expiration is
        provided, in which case the ad is republished with that deadline.
        """

    @abstractmethod
    def excluir(self, ad_id: int) -> None:
        """Delete the advertisement permanently."""

    @abstractmethod
    def renovar(self, ad_id: int, expires_at: datetime) -> Ad:
        """Publish the ad again with a new expiration deadline."""

    @abstractmethod
    def alterar_status(self, ad_id: int, status: str) -> Ad:
        """Set only the status (sold, published or expired) of the ad."""
