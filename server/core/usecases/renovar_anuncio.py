"""Renew an expired advertisement owned by the authenticated user."""

from datetime import timezone

from server.core.entities.ad import Ad
from server.core.interfaces.anuncio_editavel_repository_interface import (
    AnuncioEditavelRepositoryInterface,
)
from server.core.usecases.anuncio_do_dono import buscar_anuncio_do_dono
from server.core.usecases.erros import AnuncioNaoExpirado


class RenovarAnuncio:
    def __init__(
        self,
        anuncios: AnuncioEditavelRepositoryInterface,
        relogio,
    ) -> None:
        self._anuncios = anuncios
        self._relogio = relogio

    def executar(self, ad_id: int, usuario_id: int) -> Ad:
        anuncio = buscar_anuncio_do_dono(
            self._anuncios, ad_id, usuario_id
        )
        if anuncio.status != "expired":
            raise AnuncioNaoExpirado()

        agora = self._relogio.agora()
        if agora.tzinfo is None:
            agora = agora.replace(tzinfo=timezone.utc)
        expires_at = agora + Ad.PUBLICATION_PERIOD
        return self._anuncios.renovar(ad_id, expires_at)
