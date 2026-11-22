"""Password hashing backed by werkzeug (shipped with Flask)."""

from werkzeug.security import check_password_hash, generate_password_hash

from server.core.interfaces.hasher_de_senha_interface import (
    HasherDeSenhaInterface,
)


class HasherDeSenhaWerkzeug(HasherDeSenhaInterface):

    def gerar_hash(self, senha: str) -> str:
        return generate_password_hash(senha)

    def verificar(self, senha: str, senha_hash: str) -> bool:
        return check_password_hash(senha_hash, senha)
