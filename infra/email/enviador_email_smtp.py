"""Envio de e-mail por SMTP usando apenas a biblioteca padrão."""

import smtplib
from email.message import EmailMessage
from typing import Callable, Optional

from use_cases.autenticacao.portas import FalhaEnvioEmail

_TIMEOUT_SEGUNDOS = 10


class EnviadorEmailSmtp:
    def __init__(
        self,
        host: str,
        porta: int,
        remetente: str,
        usuario: Optional[str] = None,
        senha: Optional[str] = None,
        usar_starttls: bool = True,
        fabrica_conexao: Callable[..., smtplib.SMTP] = smtplib.SMTP,
    ) -> None:
        self._host = host
        self._porta = porta
        self._remetente = remetente
        self._usuario = usuario
        self._senha = senha
        self._usar_starttls = usar_starttls
        self._fabrica_conexao = fabrica_conexao

    def enviar(self, destinatario: str, assunto: str, corpo: str) -> None:
        mensagem = EmailMessage()
        mensagem["From"] = self._remetente
        mensagem["To"] = destinatario
        mensagem["Subject"] = assunto
        mensagem.set_content(corpo)

        try:
            with self._fabrica_conexao(
                self._host, self._porta, timeout=_TIMEOUT_SEGUNDOS
            ) as conexao:
                if self._usar_starttls:
                    conexao.starttls()
                if self._usuario:
                    conexao.login(self._usuario, self._senha or "")
                conexao.send_message(mensagem)
        except (smtplib.SMTPException, OSError) as erro:
            raise FalhaEnvioEmail(str(erro)) from erro
