"""Enviador de e-mail para desenvolvimento: escreve a mensagem no log."""

import logging

_logger = logging.getLogger(__name__)


class EnviadorEmailConsole:
    def enviar(self, destinatario: str, assunto: str, corpo: str) -> None:
        _logger.warning(
            "E-mail não enviado (SMTP não configurado).\n"
            "Para: %s\nAssunto: %s\n\n%s",
            destinatario,
            assunto,
            corpo,
        )
