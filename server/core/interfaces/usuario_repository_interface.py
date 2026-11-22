"""Repository contract consumed by user-related use cases."""

from abc import ABC, abstractmethod

from server.core.entities.usuario import Usuario


class UsuarioRepositoryInterface(ABC):
    """Persistence operations required for a user."""

    @abstractmethod
    def buscar_por_id(self, usuario_id: int) -> Usuario | None:
        """Return a user by its internal ID, or None when it does not exist."""

    @abstractmethod
    def buscar_por_email(self, email: str) -> Usuario | None:
        """Return the user with this normalized e-mail, if any."""

    @abstractmethod
    def buscar_por_identificador_alternativo(
        self, valor: str
    ) -> Usuario | None:
        """Return the user whose username or registration equals the value."""

    @abstractmethod
    def salvar(self, usuario: Usuario) -> Usuario:
        """Persist a user and return it with its internal ID."""

    @abstractmethod
    def remover(self, usuario_id: int) -> None:
        """Delete a user and the records that belong to it."""
