"""Pure domain representation of a university community member."""

import re
from dataclasses import dataclass, replace
from datetime import datetime

from server.core.entities.politicas_autenticacao import (
    DURACAO_BLOQUEIO_LOGIN,
    MAXIMO_TENTATIVAS_LOGIN,
)
from server.core.entities.vinculo import Vinculo


_EMAIL_INSTITUCIONAL_PATTERN = re.compile(
    r"[A-Z0-9!#$%&'*+/=?^_`{|}~-]+"
    r"(?:\.[A-Z0-9!#$%&'*+/=?^_`{|}~-]+)*"
    r"@(?:aluno\.)?puc-rio\.br",
    re.IGNORECASE | re.ASCII,
)


def normalizar_identificador(valor: str) -> str:
    """Normalize e-mail, username, or registration number for comparison."""
    return valor.strip().lower()


@dataclass(frozen=True)
class Usuario:
    """A member account; instances are immutable and methods return copies."""

    nome: str
    email: str
    nome_usuario: str
    vinculo: Vinculo
    senha_hash: str
    matricula: str | None = None
    confirmado_em: datetime | None = None
    tentativas_login_falhas: int = 0
    bloqueado_ate: datetime | None = None
    id: int | None = None

    def __post_init__(self) -> None:
        self._definir("nome", self.nome.strip())
        self._definir("email", normalizar_identificador(self.email))
        self._definir(
            "nome_usuario", normalizar_identificador(self.nome_usuario)
        )
        matricula = (
            normalizar_identificador(self.matricula)
            if self.matricula is not None
            else ""
        )
        self._definir("matricula", matricula or None)
        self._definir("vinculo", self._converter_vinculo(self.vinculo))

        if not self.nome:
            raise ValueError("Nome é obrigatório.")
        if _EMAIL_INSTITUCIONAL_PATTERN.fullmatch(self.email) is None:
            raise ValueError(
                "Email deve ser válido e usar os domínios institucionais "
                "PUC-Rio."
            )
        if not self.nome_usuario:
            raise ValueError("Nome de usuário é obrigatório.")
        if "@" in self.nome_usuario:
            raise ValueError("Nome de usuário não pode conter '@'.")
        if not self.senha_hash:
            raise ValueError("Hash da senha é obrigatório.")
        if self.tentativas_login_falhas < 0:
            raise ValueError("Tentativas de login não podem ser negativas.")

    def esta_confirmado(self) -> bool:
        return self.confirmado_em is not None

    def esta_bloqueado(self, agora: datetime) -> bool:
        return self.bloqueado_ate is not None and agora < self.bloqueado_ate

    def confirmar(self, agora: datetime) -> "Usuario":
        return replace(self, confirmado_em=agora)

    def registrar_falha_de_login(self, agora: datetime) -> "Usuario":
        """Count a failed login; the last allowed failure locks the account."""
        tentativas = self.tentativas_login_falhas + 1
        if tentativas >= MAXIMO_TENTATIVAS_LOGIN:
            return replace(
                self,
                tentativas_login_falhas=0,
                bloqueado_ate=agora + DURACAO_BLOQUEIO_LOGIN,
            )
        return replace(self, tentativas_login_falhas=tentativas)

    def registrar_login_bem_sucedido(self) -> "Usuario":
        return replace(self, tentativas_login_falhas=0, bloqueado_ate=None)

    def _definir(self, campo: str, valor: object) -> None:
        object.__setattr__(self, campo, valor)

    @staticmethod
    def _converter_vinculo(vinculo: Vinculo | str) -> Vinculo:
        try:
            return Vinculo(vinculo)
        except ValueError:
            raise ValueError(
                "Vínculo deve ser aluno ou funcionário."
            ) from None
