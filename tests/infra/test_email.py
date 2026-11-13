import logging
import smtplib

import pytest

from infra.email.enviador_email_console import EnviadorEmailConsole
from infra.email.enviador_email_smtp import EnviadorEmailSmtp
from use_cases.autenticacao.portas import FalhaEnvioEmail


class ConexaoSmtpFalsa:
    def __init__(self, host, porta, timeout):
        self.host = host
        self.porta = porta
        self.timeout = timeout
        self.chamadas = []
        self.mensagens = []
        ConexaoSmtpFalsa.ultima = self

    def __enter__(self):
        return self

    def __exit__(self, *excecao):
        return False

    def starttls(self):
        self.chamadas.append("starttls")

    def login(self, usuario, senha):
        self.chamadas.append(("login", usuario, senha))

    def send_message(self, mensagem):
        self.mensagens.append(mensagem)


def criar_enviador(**sobrescritas):
    dados = {
        "host": "smtp.exemplo.com",
        "porta": 587,
        "remetente": "nao-responda@exemplo.com",
        "usuario": "app",
        "senha": "segredo",
        "fabrica_conexao": ConexaoSmtpFalsa,
    }
    dados.update(sobrescritas)
    return EnviadorEmailSmtp(**dados)


def test_smtp_envia_mensagem_com_tls_e_login():
    criar_enviador().enviar("ana@puc-rio.br", "Assunto", "Corpo")

    conexao = ConexaoSmtpFalsa.ultima
    assert (conexao.host, conexao.porta) == ("smtp.exemplo.com", 587)
    assert conexao.chamadas == ["starttls", ("login", "app", "segredo")]
    [mensagem] = conexao.mensagens
    assert mensagem["To"] == "ana@puc-rio.br"
    assert mensagem["From"] == "nao-responda@exemplo.com"
    assert mensagem["Subject"] == "Assunto"
    assert mensagem.get_content().strip() == "Corpo"


def test_smtp_sem_usuario_nem_tls_nao_faz_login():
    criar_enviador(usuario=None, usar_starttls=False).enviar(
        "ana@puc-rio.br", "Assunto", "Corpo"
    )

    assert ConexaoSmtpFalsa.ultima.chamadas == []


@pytest.mark.parametrize(
    "erro", [smtplib.SMTPAuthenticationError(535, b"x"), OSError("rede")]
)
def test_falha_do_smtp_vira_falha_envio_email(erro):
    def fabrica_com_erro(*args, **kwargs):
        raise erro

    with pytest.raises(FalhaEnvioEmail):
        criar_enviador(fabrica_conexao=fabrica_com_erro).enviar(
            "ana@puc-rio.br", "Assunto", "Corpo"
        )


def test_console_registra_o_email_no_log(caplog):
    with caplog.at_level(logging.WARNING):
        EnviadorEmailConsole().enviar("ana@puc-rio.br", "Assunto", "Corpo")

    assert "ana@puc-rio.br" in caplog.text
    assert "Corpo" in caplog.text
