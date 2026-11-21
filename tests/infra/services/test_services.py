import logging
import ssl
from datetime import UTC, timedelta

import pytest

from server.infra.services import enviador_email_smtp
from server.infra.services.enviador_email_log import EnviadorDeEmailLog
from server.infra.services.enviador_email_smtp import (
    ConfiguracaoSMTP,
    EnviadorDeEmailSMTP,
)
from server.infra.services.gerador_token_secrets import GeradorDeTokenSecrets
from server.infra.services.hasher_senha_werkzeug import HasherDeSenhaWerkzeug
from server.infra.services.relogio_sistema import RelogioSistema


def test_werkzeug_hasher_hashes_and_verifies():
    hasher = HasherDeSenhaWerkzeug()

    senha_hash = hasher.gerar_hash("senha-segura")

    assert senha_hash != "senha-segura"
    assert hasher.gerar_hash("senha-segura") != senha_hash
    assert hasher.verificar("senha-segura", senha_hash)
    assert not hasher.verificar("senha-errada", senha_hash)


def test_secrets_token_generator_returns_unique_url_safe_tokens():
    gerador = GeradorDeTokenSecrets()

    tokens = {gerador.gerar() for _ in range(20)}

    assert len(tokens) == 20
    assert all(len(token) >= 43 for token in tokens)
    assert all(
        token.replace("-", "").replace("_", "").isalnum() for token in tokens
    )


def test_system_clock_returns_utc():
    agora = RelogioSistema().agora()

    assert agora.tzinfo is not None
    assert agora.utcoffset() == timedelta(0)
    assert agora.tzinfo == UTC


def test_log_email_sender_writes_message_to_log(caplog):
    with caplog.at_level(logging.INFO):
        EnviadorDeEmailLog().enviar(
            "ana@aluno.puc-rio.br", "Assunto", "link?token=abc"
        )

    assert "ana@aluno.puc-rio.br" in caplog.text
    assert "Assunto" in caplog.text
    assert "link?token=abc" in caplog.text


class SMTPFalso:
    instancias: list["SMTPFalso"] = []

    def __init__(self, host, porta, timeout):
        self.host, self.porta, self.timeout = host, porta, timeout
        self.chamadas = []
        self.mensagens = []
        SMTPFalso.instancias.append(self)

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.chamadas.append("quit")
        return False

    def starttls(self, context):
        assert isinstance(context, ssl.SSLContext)
        self.chamadas.append("starttls")

    def login(self, usuario, senha):
        self.chamadas.append(("login", usuario, senha))

    def send_message(self, mensagem):
        self.chamadas.append("send_message")
        self.mensagens.append(mensagem)


@pytest.fixture
def smtp_falso(monkeypatch):
    SMTPFalso.instancias = []
    monkeypatch.setattr(enviador_email_smtp.smtplib, "SMTP", SMTPFalso)
    return SMTPFalso


def test_smtp_sender_uses_starttls_login_and_sends_message(smtp_falso):
    enviador = EnviadorDeEmailSMTP(
        ConfiguracaoSMTP(
            host="smtp.example",
            porta=587,
            usuario="user",
            senha="secret",
            remetente="noreply@example.com",
        )
    )

    enviador.enviar("ana@aluno.puc-rio.br", "Assunto", "Corpo do e-mail")

    [smtp] = smtp_falso.instancias
    assert (smtp.host, smtp.porta) == ("smtp.example", 587)
    assert smtp.chamadas == [
        "starttls", ("login", "user", "secret"), "send_message", "quit",
    ]
    [mensagem] = smtp.mensagens
    assert mensagem["From"] == "noreply@example.com"
    assert mensagem["To"] == "ana@aluno.puc-rio.br"
    assert mensagem["Subject"] == "Assunto"
    assert mensagem.get_content().strip() == "Corpo do e-mail"
