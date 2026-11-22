"""Authenticated session identified by an opaque token (hash only)."""

from dataclasses import dataclass, replace
from datetime import datetime


@dataclass(frozen=True)
class Sessao:
    usuario_id: int
    token_hash: str
    criada_em: datetime
    expira_em: datetime
    revogada_em: datetime | None = None
    id: int | None = None

    def esta_ativa(self, agora: datetime) -> bool:
        return self.revogada_em is None and agora < self.expira_em

    def revogar(self, agora: datetime) -> "Sessao":
        return replace(self, revogada_em=agora)
