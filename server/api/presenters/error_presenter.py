"""Schema for HTTP representations of expected errors."""

from pydantic import BaseModel, ValidationError


class ErrorSchema(BaseModel):
    """Public error response shape.

    `code` is only set when the client must react to a specific situation,
    such as offering to resend the confirmation link.
    """

    message: str
    code: str | None = None


def apresenta_erro(message: str, code: str | None = None) -> ErrorSchema:
    """Build an explicit error response model."""
    return ErrorSchema(message=message, code=code)


def apresenta_erro_de_validacao(erro: ValidationError) -> ErrorSchema:
    """Summarize request validation errors by field."""
    campos = sorted(
        {
            ".".join(str(parte) for parte in detalhe["loc"])
            for detalhe in erro.errors()
        }
    )
    return apresenta_erro(
        "Campos ausentes ou inválidos: " + ", ".join(campos) + "."
    )
