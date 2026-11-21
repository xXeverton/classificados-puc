"""Single-use e-mail confirmation token (only its hash is kept)."""

from dataclasses import dataclass, replace
from datetime import datetime


@dataclass(frozen=True)
class TokenDeConfirmacao:
    usuario_id: int
    token_hash: str
    expira_em: datetime
    usado_em: datetime | None = None
    id: int | None = None

    def foi_usado(self) -> bool:
        return self.usado_em is not None

    def esta_expirado(self, agora: datetime) -> bool:
        return agora > self.expira_em

    def esta_valido(self, agora: datetime) -> bool:
        return not self.foi_usado() and not self.esta_expirado(agora)

    def usar(self, agora: datetime) -> "TokenDeConfirmacao":
        if not self.esta_valido(agora):
            raise ValueError("Token de confirmação não está válido.")
        return replace(self, usado_em=agora)
