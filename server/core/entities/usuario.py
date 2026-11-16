"""Pure domain representation of a university community member."""

import re
from dataclasses import dataclass


_EMAIL_INSTITUCIONAL_PATTERN = re.compile(
    r"[A-Z0-9!#$%&'*+/=?^_`{|}~-]+"
    r"(?:\.[A-Z0-9!#$%&'*+/=?^_`{|}~-]+)*"
    r"@(?:aluno\.)?puc-rio\.br",
    re.IGNORECASE | re.ASCII,
)


@dataclass(frozen=True)
class Usuario:
    """A user identified by the fields currently persisted by the project."""

    nome: str
    email: str
    matricula: str
    vinculo: str
    id: int | None = None

    def __post_init__(self) -> None:
        if _EMAIL_INSTITUCIONAL_PATTERN.fullmatch(self.email) is None:
            raise ValueError(
                "Email deve ser válido e usar os domínios institucionais "
                "PUC-Rio."
            )
