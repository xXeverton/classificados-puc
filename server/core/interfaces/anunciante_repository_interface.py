"""Repository contract for advertiser profiles."""

from abc import ABC, abstractmethod

from server.core.entities.anunciante import Anunciante


class AnuncianteRepositoryInterface(ABC):

    @abstractmethod
    def buscar_por_usuario_id(self, usuario_id: int) -> Anunciante | None:
        """Return the advertiser profile of this user, if there is one."""

    @abstractmethod
    def salvar(self, anunciante: Anunciante) -> Anunciante:
        """Create or update the profile of ``anunciante.usuario_id``."""
