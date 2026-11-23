"""List the upcoming events shown in the home highlights (spec 015)."""

from server.core.entities.ad import Ad
from server.core.entities.prazo_do_evento import dia_de_hoje
from server.core.entities.usuario import Usuario
from server.core.interfaces.eventos_em_destaque_repository_interface import (
    EventosEmDestaqueRepository,
)
from server.core.interfaces.relogio_interface import RelogioInterface
from server.core.usecases.erros import UsuarioNaoAutenticado

LIMITE_EVENTOS_EM_DESTAQUE = 5


class ListarEventosEmDestaque:
    def __init__(
        self,
        eventos: EventosEmDestaqueRepository,
        relogio: RelogioInterface,
    ) -> None:
        self._eventos = eventos
        self._relogio = relogio

    def executar(self, usuario: Usuario | None) -> list[Ad]:
        if usuario is None:
            raise UsuarioNaoAutenticado()
        hoje = dia_de_hoje(self._relogio.agora())
        return self._eventos.listar_eventos_futuros(
            hoje, LIMITE_EVENTOS_EM_DESTAQUE
        )
