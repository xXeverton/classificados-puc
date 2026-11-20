"""Resolve the logged-in user from a session token."""

from server.core.entities.politicas_autenticacao import hash_de_token
from server.core.entities.usuario import Usuario
from server.core.interfaces.relogio_interface import RelogioInterface
from server.core.interfaces.sessao_repository_interface import (
    SessaoRepositoryInterface,
)
from server.core.interfaces.usuario_repository_interface import (
    UsuarioRepositoryInterface,
)
from server.core.usecases.erros import SessaoInvalida


class ObterUsuarioDaSessao:

    def __init__(
        self,
        sessoes: SessaoRepositoryInterface,
        usuarios: UsuarioRepositoryInterface,
        relogio: RelogioInterface,
    ) -> None:
        self._sessoes = sessoes
        self._usuarios = usuarios
        self._relogio = relogio

    def executar(self, token: str) -> Usuario:
        sessao = self._sessoes.buscar_por_hash(hash_de_token(token))
        if sessao is None or not sessao.esta_ativa(self._relogio.agora()):
            raise SessaoInvalida()
        usuario = self._usuarios.buscar_por_id(sessao.usuario_id)
        if usuario is None or not usuario.esta_confirmado():
            raise SessaoInvalida()
        return usuario
