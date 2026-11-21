"""Read the advertiser profile of a user."""

from server.core.entities.anunciante import Anunciante
from server.core.interfaces.anunciante_repository_interface import (
    AnuncianteRepositoryInterface,
)
from server.core.usecases.erros import PerfilNaoEncontrado


class ObterPerfilAnunciante:

    def __init__(self, anunciantes: AnuncianteRepositoryInterface) -> None:
        self._anunciantes = anunciantes

    def executar(self, usuario_id: int) -> Anunciante:
        anunciante = self._anunciantes.buscar_por_usuario_id(usuario_id)
        if anunciante is None:
            raise PerfilNaoEncontrado()
        return anunciante
