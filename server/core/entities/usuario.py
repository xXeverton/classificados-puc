"""Pure domain representation of a university community member."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Usuario:
    """A user identified by the fields currently persisted by the project."""

    nome: str
    email: str
    matricula: str
    vinculo: str
    id: int | None = None
