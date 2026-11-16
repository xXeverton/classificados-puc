"""Entidade Usuario e seus vínculos institucionais."""

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class Vinculo(str, Enum):
    ALUNO = "aluno"
    FUNCIONARIO = "funcionario"
    TERCEIRIZADO = "terceirizado"


VINCULOS_COM_ACESSO = frozenset({Vinculo.ALUNO, Vinculo.FUNCIONARIO})


@dataclass(frozen=True)
class Usuario:
    id: int
    nome: str
    email: str
    matricula: str
    vinculo: Vinculo
    senha_hash: Optional[str] = None

    def pode_acessar(self) -> bool:
        """Terceirizados ficam fora da plataforma por ora (RN2)."""
        return self.vinculo in VINCULOS_COM_ACESSO
