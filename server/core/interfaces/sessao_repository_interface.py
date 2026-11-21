"""Repository contract for authenticated sessions."""

from abc import ABC, abstractmethod

from server.core.entities.sessao import Sessao


class SessaoRepositoryInterface(ABC):

    @abstractmethod
    def salvar(self, sessao: Sessao) -> Sessao:
        """Persist a session and return it with its internal ID."""

    @abstractmethod
    def buscar_por_hash(self, token_hash: str) -> Sessao | None:
        """Return the session stored with this token hash, if any."""
