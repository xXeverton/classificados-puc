"""E-mail sender over SMTP with STARTTLS."""

import smtplib
import ssl
from dataclasses import dataclass
from email.message import EmailMessage

from server.core.interfaces.enviador_de_email_interface import (
    EnviadorDeEmailInterface,
)

TIMEOUT_SEGUNDOS = 10


@dataclass(frozen=True)
class ConfiguracaoSMTP:
    host: str
    porta: int
    usuario: str
    senha: str
    remetente: str


class EnviadorDeEmailSMTP(EnviadorDeEmailInterface):

    def __init__(self, configuracao: ConfiguracaoSMTP) -> None:
        self._configuracao = configuracao

    def enviar(self, destinatario: str, assunto: str, corpo: str) -> None:
        mensagem = EmailMessage()
        mensagem["From"] = self._configuracao.remetente
        mensagem["To"] = destinatario
        mensagem["Subject"] = assunto
        mensagem.set_content(corpo)

        with smtplib.SMTP(
            self._configuracao.host,
            self._configuracao.porta,
            timeout=TIMEOUT_SEGUNDOS,
        ) as smtp:
            smtp.starttls(context=ssl.create_default_context())
            smtp.login(self._configuracao.usuario, self._configuracao.senha)
            smtp.send_message(mensagem)
