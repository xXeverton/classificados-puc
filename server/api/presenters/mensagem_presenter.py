"""Plain informational message."""

from pydantic import BaseModel


class MensagemViewSchema(BaseModel):
    message: str


def apresenta_mensagem(message: str) -> MensagemViewSchema:
    return MensagemViewSchema(message=message)
