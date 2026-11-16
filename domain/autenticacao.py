"""Regras de negócio da autenticação: bloqueio por tentativas e link mágico."""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional

MAX_TENTATIVAS_LOGIN = 5
DURACAO_BLOQUEIO_LOGIN = timedelta(minutes=10)
VALIDADE_LINK_MAGICO = timedelta(minutes=15)


@dataclass(frozen=True)
class PoliticaBloqueio:
    max_tentativas: int = MAX_TENTATIVAS_LOGIN
    duracao: timedelta = DURACAO_BLOQUEIO_LOGIN


@dataclass(frozen=True)
class TentativasLogin:
    """Falhas consecutivas de login de uma matrícula (RN3)."""

    falhas_consecutivas: int = 0
    bloqueado_ate: Optional[datetime] = None

    def esta_bloqueado(self, agora: datetime) -> bool:
        return self.bloqueado_ate is not None and agora < self.bloqueado_ate

    def registrar_falha(
        self, agora: datetime, politica: PoliticaBloqueio
    ) -> "TentativasLogin":
        # Um bloqueio já encerrado não conta para o próximo: recomeça do zero.
        falhas_anteriores = (
            0 if self.bloqueado_ate is not None else self.falhas_consecutivas
        )
        falhas = falhas_anteriores + 1
        if falhas >= politica.max_tentativas:
            return TentativasLogin(falhas, agora + politica.duracao)
        return TentativasLogin(falhas, None)


@dataclass(frozen=True)
class LinkMagico:
    """Link de acesso por e-mail. Só o hash do token é guardado."""

    token_hash: str
    usuario_id: int
    expira_em: datetime
    usado: bool = False

    def pode_ser_usado(self, agora: datetime) -> bool:
        return not self.usado and agora < self.expira_em
