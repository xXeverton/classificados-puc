"""Interfaces que os casos de uso de autenticação consomem.

As implementações concretas ficam em `infra/`.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Protocol

from domain.autenticacao import LinkMagico, TentativasLogin
from domain.usuario import Usuario


@dataclass(frozen=True)
class SessaoAutenticada:
    token: str
    expira_em_segundos: int


class FalhaEnvioEmail(Exception):
    """O provedor de e-mail não conseguiu entregar a mensagem."""


class UsuarioRepository(Protocol):
    def buscar_por_email(self, email: str) -> Optional[Usuario]: ...

    def buscar_por_id(self, usuario_id: int) -> Optional[Usuario]: ...


class TentativasLoginRepository(Protocol):
    """Tentativas de login indexadas pelo e-mail normalizado."""

    def obter(self, email: str) -> TentativasLogin: ...

    def salvar(self, email: str, tentativas: TentativasLogin) -> None: ...

    def limpar(self, email: str) -> None: ...


class LinkMagicoRepository(Protocol):
    def salvar(self, link: LinkMagico) -> None: ...

    def buscar_por_token_hash(
        self, token_hash: str
    ) -> Optional[LinkMagico]: ...

    def marcar_como_usado(self, token_hash: str) -> None: ...


class VerificadorSenha(Protocol):
    def verificar(self, senha: str, senha_hash: str) -> bool: ...


class ServicoToken(Protocol):
    def emitir(self, usuario_id: int) -> SessaoAutenticada: ...

    def validar(self, token: str) -> int:
        """Retorna o id do usuário ou levanta `TokenInvalido`."""
        ...


class EnviadorEmail(Protocol):
    def enviar(self, destinatario: str, assunto: str, corpo: str) -> None:
        """Envia o e-mail ou levanta `FalhaEnvioEmail`."""
        ...


class Relogio(Protocol):
    def agora(self) -> datetime: ...
