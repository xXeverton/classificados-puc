"""Public representation of a user (never exposes the password hash)."""

from pydantic import BaseModel

from server.core.entities.usuario import Usuario


class UsuarioViewSchema(BaseModel):
    id: int
    nome: str
    email: str
    nome_usuario: str
    matricula: str | None
    vinculo: str
    email_confirmado: bool


def apresenta_usuario(usuario: Usuario) -> UsuarioViewSchema:
    return UsuarioViewSchema(
        id=usuario.id,
        nome=usuario.nome,
        email=usuario.email,
        nome_usuario=usuario.nome_usuario,
        matricula=usuario.matricula,
        vinculo=usuario.vinculo.value,
        email_confirmado=usuario.esta_confirmado(),
    )
