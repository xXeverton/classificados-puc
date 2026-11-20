"""Confirm an account through the single-use link sent by e-mail."""

from server.core.entities.politicas_autenticacao import hash_de_token
from server.core.entities.usuario import Usuario
from server.core.interfaces.relogio_interface import RelogioInterface
from server.core.interfaces.token_de_confirmacao_repository_interface import (
    TokenDeConfirmacaoRepositoryInterface,
)
from server.core.interfaces.usuario_repository_interface import (
    UsuarioRepositoryInterface,
)
from server.core.usecases.erros import TokenExpirado, TokenInvalido


class ConfirmarEmail:

    def __init__(
        self,
        usuarios: UsuarioRepositoryInterface,
        tokens: TokenDeConfirmacaoRepositoryInterface,
        relogio: RelogioInterface,
    ) -> None:
        self._usuarios = usuarios
        self._tokens = tokens
        self._relogio = relogio

    def executar(self, token: str) -> Usuario:
        agora = self._relogio.agora()
        registro = self._tokens.buscar_por_hash(hash_de_token(token))
        if registro is None or registro.foi_usado():
            raise TokenInvalido()
        if registro.esta_expirado(agora):
            raise TokenExpirado()
        usuario = self._usuarios.buscar_por_id(registro.usuario_id)
        if usuario is None:
            raise TokenInvalido()

        self._tokens.salvar(registro.usar(agora))
        return self._usuarios.salvar(usuario.confirmar(agora))
