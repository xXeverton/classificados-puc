"""Issue a new e-mail confirmation link, invalidating the previous ones."""

from server.core.entities.politicas_autenticacao import (
    VALIDADE_TOKEN_CONFIRMACAO,
    hash_de_token,
)
from server.core.entities.token_de_confirmacao import TokenDeConfirmacao
from server.core.entities.usuario import Usuario
from server.core.interfaces.enviador_de_email_interface import (
    EnviadorDeEmailInterface,
)
from server.core.interfaces.gerador_de_token_interface import (
    GeradorDeTokenInterface,
)
from server.core.interfaces.relogio_interface import RelogioInterface
from server.core.interfaces.token_de_confirmacao_repository_interface import (
    TokenDeConfirmacaoRepositoryInterface,
)

ASSUNTO_CONFIRMACAO = "Confirme seu e-mail - Classificados PUC"


class EmissorDeConfirmacao:

    def __init__(
        self,
        tokens: TokenDeConfirmacaoRepositoryInterface,
        gerador_token: GeradorDeTokenInterface,
        enviador_email: EnviadorDeEmailInterface,
        relogio: RelogioInterface,
        url_base: str,
    ) -> None:
        self._tokens = tokens
        self._gerador_token = gerador_token
        self._enviador_email = enviador_email
        self._relogio = relogio
        self._url_base = url_base

    def emitir(self, usuario: Usuario) -> None:
        if usuario.id is None:
            raise ValueError("Usuário precisa estar salvo para receber link.")
        agora = self._relogio.agora()
        self._tokens.invalidar_do_usuario(usuario.id, agora)

        token = self._gerador_token.gerar()
        self._tokens.salvar(
            TokenDeConfirmacao(
                usuario_id=usuario.id,
                token_hash=hash_de_token(token),
                expira_em=agora + VALIDADE_TOKEN_CONFIRMACAO,
            )
        )
        self._enviador_email.enviar(
            usuario.email, ASSUNTO_CONFIRMACAO, self._corpo(usuario, token)
        )

    def _corpo(self, usuario: Usuario, token: str) -> str:
        minutos = int(VALIDADE_TOKEN_CONFIRMACAO.total_seconds() // 60)
        return (
            f"Olá, {usuario.nome}!\n\n"
            "Para concluir seu cadastro nos Classificados PUC, confirme seu "
            "e-mail abrindo o link abaixo:\n\n"
            f"{self._link(token)}\n\n"
            f"O link vale por {minutos} minutos e pode ser usado uma única "
            "vez. Se você não fez este cadastro, ignore esta mensagem.\n"
        )

    def _link(self, token: str) -> str:
        separador = "&" if "?" in self._url_base else "?"
        return f"{self._url_base}{separador}token={token}"
