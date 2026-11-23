"""Let the owner change the editable fields of an advertisement."""

from datetime import timezone

from server.core.entities.ad import Ad
from server.core.entities.anuncio import Anuncio, CATEGORIA_EVENTO
from server.core.entities.prazo_do_evento import (
    dia_de_hoje,
    fim_do_prazo_do_evento,
)
from server.core.interfaces.anuncio_editavel_repository_interface import (
    AnuncioEditavelRepositoryInterface,
)
from server.core.usecases.anuncio_do_dono import buscar_anuncio_do_dono
from server.core.usecases.erros import (
    CategoriaNaoEditavel,
    DataDeEventoInvalida,
)


class EditarAnuncio:
    def __init__(
        self,
        anuncios: AnuncioEditavelRepositoryInterface,
        relogio,
    ) -> None:
        self._anuncios = anuncios
        self._relogio = relogio

    def executar(self, ad_id: int, anuncio: Anuncio) -> Ad:
        """Save `anuncio` over the ad; `anuncio.usuario_id` is the editor."""
        atual = buscar_anuncio_do_dono(
            self._anuncios, ad_id, anuncio.usuario_id
        )
        # The category defines the ad type and which fields apply (RN3).
        if anuncio.categoria != atual.category:
            raise CategoriaNaoEditavel()
        expires_at = None
        if anuncio.categoria == CATEGORIA_EVENTO:
            if anuncio.data_evento < dia_de_hoje(self._relogio.agora()):
                raise DataDeEventoInvalida()
            # The period follows the event day, so a new day moves it
            # (spec 015, CA8). A sold event keeps its status and period.
            if atual.status in ("published", "expired"):
                expires_at = fim_do_prazo_do_evento(anuncio.data_evento)
        elif atual.status == "expired":
            agora = self._relogio.agora()
            if agora.tzinfo is None:
                agora = agora.replace(tzinfo=timezone.utc)
            expires_at = agora + Ad.PUBLICATION_PERIOD
        return self._anuncios.atualizar(
            ad_id,
            anuncio,
            expires_at=expires_at,
        )
