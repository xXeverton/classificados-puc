"""Erros de negócio da autenticação."""

MENSAGEM_CREDENCIAIS_INVALIDAS = "E-mail ou senha inválidos"
MENSAGEM_EMAIL_NAO_INSTITUCIONAL = (
    "Use seu e-mail institucional (@aluno.puc-rio.br ou @puc-rio.br)."
)


class ErroAutenticacao(Exception):
    """Base dos erros de autenticação."""


class CredenciaisInvalidas(ErroAutenticacao):
    def __init__(self) -> None:
        super().__init__(MENSAGEM_CREDENCIAIS_INVALIDAS)


class EmailNaoInstitucional(ErroAutenticacao):
    def __init__(self) -> None:
        super().__init__(MENSAGEM_EMAIL_NAO_INSTITUCIONAL)


class LoginBloqueado(ErroAutenticacao):
    def __init__(self, segundos_restantes: int) -> None:
        super().__init__(
            "Login bloqueado temporariamente por excesso de tentativas."
        )
        self.segundos_restantes = segundos_restantes


class TokenInvalido(ErroAutenticacao):
    def __init__(self) -> None:
        super().__init__("Token inválido ou expirado")
