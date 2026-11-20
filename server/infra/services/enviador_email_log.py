"""E-mail sender for development and tests: writes the message to the log."""

import logging

from server.core.interfaces.enviador_de_email_interface import (
    EnviadorDeEmailInterface,
)

logger = logging.getLogger(__name__)


class EnviadorDeEmailLog(EnviadorDeEmailInterface):

    def enviar(self, destinatario: str, assunto: str, corpo: str) -> None:
        logger.info(
            "E-mail (backend log)\nPara: %s\nAssunto: %s\n\n%s",
            destinatario,
            assunto,
            corpo,
        )
