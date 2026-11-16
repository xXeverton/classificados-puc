"""Hash e verificação de senhas com `werkzeug.security` (RN7)."""

from werkzeug.security import check_password_hash, generate_password_hash


class VerificadorSenhaWerkzeug:
    def gerar_hash(self, senha: str) -> str:
        return generate_password_hash(senha)

    def verificar(self, senha: str, senha_hash: str) -> bool:
        return check_password_hash(senha_hash, senha)
