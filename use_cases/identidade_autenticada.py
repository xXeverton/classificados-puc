"""Porta de autenticação usada pelas rotas da aplicação."""

from dataclasses import dataclass
from typing import Protocol

CHAVE_EXTENSAO_AUTENTICADOR = "autenticador"


@dataclass(frozen=True)
class UsuarioAutenticado:
    """Identidade mínima disponibilizada à aplicação."""

    id_usuario: int
    nome_exibicao: str


class Autenticador(Protocol):
    def usuario_atual(self) -> UsuarioAutenticado | None:
        """Retorna o usuário da requisição ou None quando não autenticado."""
