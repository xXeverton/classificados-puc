"""Publish an announcement for a complete advertiser profile."""

from datetime import timedelta

from server.core.entities.ad import Ad
from server.core.entities.anuncio import (
    Anuncio,
    CATEGORIA_EVENTO,
    PRAZO_EXPIRACAO_DIAS,
)
from server.core.entities.prazo_do_evento import (
    dia_de_hoje,
    fim_do_prazo_do_evento,
)
from server.core.interfaces.ad_repository_interface import AdRepository
from server.core.interfaces.anunciante_repository_interface import (
    AnuncianteRepositoryInterface,
)
from server.core.interfaces.relogio_interface import RelogioInterface
from server.core.usecases.erros import (
    DataDeEventoInvalida,
    PerfilIncompleto,
)


class PublicarAnuncio:
    def __init__(
        self,
        anuncios: AdRepository,
        anunciantes: AnuncianteRepositoryInterface,
        relogio: RelogioInterface,
    ) -> None:
        self._anuncios = anuncios
        self._anunciantes = anunciantes
        self._relogio = relogio

    def executar(self, anuncio: Anuncio) -> Ad:
        anunciante = self._anunciantes.buscar_por_usuario_id(
            anuncio.usuario_id
        )
        if anunciante is None:
            raise PerfilIncompleto()
        criado_em = self._relogio.agora()
        if anuncio.categoria == CATEGORIA_EVENTO:
            # An event lasts until the day after it happens (D-009).
            if anuncio.data_evento < dia_de_hoje(criado_em):
                raise DataDeEventoInvalida()
            expira_em = fim_do_prazo_do_evento(anuncio.data_evento)
        else:
            expira_em = criado_em + timedelta(days=PRAZO_EXPIRACAO_DIAS)
        return self._anuncios.publish(
            anuncio,
            anunciante.nome_exibicao,
            criado_em,
            expira_em,
        )
