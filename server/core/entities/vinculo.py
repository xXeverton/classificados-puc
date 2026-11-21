"""Institutional relationship of a member with PUC-Rio."""

from enum import Enum


class Vinculo(Enum):
    """Relationships accepted at registration."""

    ALUNO = "aluno"
    FUNCIONARIO = "funcionario"
