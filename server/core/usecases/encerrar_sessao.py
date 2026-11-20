"""Log out by revoking the session on the server."""

from server.core.entities.politicas_autenticacao import hash_de_token
from server.core.interfaces.relogio_interface import RelogioInterface
from server.core.interfaces.sessao_repository_interface import (
    SessaoRepositoryInterface,
)
from server.core.usecases.erros import SessaoInvalida


class EncerrarSessao:

    def __init__(
        self, sessoes: SessaoRepositoryInterface, relogio: RelogioInterface
    ) -> None:
        self._sessoes = sessoes
        self._relogio = relogio

    def executar(self, token: str) -> None:
        agora = self._relogio.agora()
        sessao = self._sessoes.buscar_por_hash(hash_de_token(token))
        if sessao is None or not sessao.esta_ativa(agora):
            raise SessaoInvalida()
        self._sessoes.salvar(sessao.revogar(agora))
