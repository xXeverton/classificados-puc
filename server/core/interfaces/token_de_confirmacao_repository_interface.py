"""Repository contract for e-mail confirmation tokens."""

from abc import ABC, abstractmethod
from datetime import datetime

from server.core.entities.token_de_confirmacao import TokenDeConfirmacao


class TokenDeConfirmacaoRepositoryInterface(ABC):

    @abstractmethod
    def salvar(self, token: TokenDeConfirmacao) -> TokenDeConfirmacao:
        """Persist a token and return it with its internal ID."""

    @abstractmethod
    def buscar_por_hash(self, token_hash: str) -> TokenDeConfirmacao | None:
        """Return the token stored with this hash, if any."""

    @abstractmethod
    def invalidar_do_usuario(self, usuario_id: int, agora: datetime) -> None:
        """Mark every unused token of the user as used at `agora`."""

    @abstractmethod
    def existe_valido_do_usuario(
        self, usuario_id: int, agora: datetime
    ) -> bool:
        """Tell whether the user has an unused, unexpired token."""
