"""Repository contract consumed by user-related use cases."""

from abc import ABC, abstractmethod

from server.core.entities.usuario import Usuario


class UsuarioRepositoryInterface(ABC):
    """Persistence operations required for a user."""

    @abstractmethod
    def buscar_por_id(self, usuario_id: int) -> Usuario | None:
        """Return a user by its internal ID, or None when it does not exist."""

    @abstractmethod
    def salvar(self, usuario: Usuario) -> Usuario:
        """Persist a user and return it with its internal ID."""
