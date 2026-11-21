"""Errors raised by application use cases (no HTTP knowledge)."""


class ErroDeCasoDeUso(Exception):
    """Base class for expected business failures."""

    mensagem_padrao = "Operação não permitida."

    def __init__(self, mensagem: str | None = None) -> None:
        super().__init__(mensagem or self.mensagem_padrao)

    @property
    def mensagem(self) -> str:
        return str(self)


class DadosInvalidos(ErroDeCasoDeUso):
    mensagem_padrao = "Dados inválidos."


class EmailEmUso(ErroDeCasoDeUso):
    mensagem_padrao = "E-mail já está em uso."


class IdentificadorEmUso(ErroDeCasoDeUso):
    mensagem_padrao = "Identificador já está em uso."


class TokenInvalido(ErroDeCasoDeUso):
    mensagem_padrao = "Link de confirmação inválido ou já utilizado."


class TokenExpirado(ErroDeCasoDeUso):
    mensagem_padrao = (
        "Link de confirmação expirado. Solicite um novo link."
    )


class CredenciaisInvalidas(ErroDeCasoDeUso):
    mensagem_padrao = "Credenciais inválidas"


class ContaBloqueada(ErroDeCasoDeUso):
    mensagem_padrao = (
        "Login bloqueado temporariamente após várias tentativas. "
        "Tente novamente em alguns minutos."
    )


class EmailNaoConfirmado(ErroDeCasoDeUso):
    mensagem_padrao = (
        "Confirme seu e-mail para entrar. Você pode solicitar um novo link."
    )


class SessaoInvalida(ErroDeCasoDeUso):
    mensagem_padrao = "Sessão inválida ou expirada."


class PerfilNaoEncontrado(ErroDeCasoDeUso):
    mensagem_padrao = "Perfil de anunciante não encontrado."


class FotoInvalida(ErroDeCasoDeUso):
    mensagem_padrao = "Foto inválida."
