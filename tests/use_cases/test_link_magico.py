from datetime import timedelta
from urllib.parse import parse_qs, urlparse

import pytest

from domain.erros import EmailNaoInstitucional, TokenInvalido
from domain.usuario import Vinculo
from infra.repositories.memoria import (
    LinkMagicoRepositoryMemoria,
    UsuarioRepositoryMemoria,
)
from tests.fakes import (
    EnviadorEmailFalso,
    RelogioControlado,
    ServicoTokenFalso,
    criar_usuario,
)
from use_cases.autenticacao import EntrarComLinkMagico, SolicitarLinkMagico
from use_cases.autenticacao.link_magico import ASSUNTO_LINK_MAGICO

URL_BASE = "https://classificados.puc/entrar/link"
EMAIL = "ana@aluno.puc-rio.br"


@pytest.fixture
def relogio():
    return RelogioControlado()


@pytest.fixture
def usuarios():
    return UsuarioRepositoryMemoria([criar_usuario()])


@pytest.fixture
def links():
    return LinkMagicoRepositoryMemoria()


@pytest.fixture
def enviador():
    return EnviadorEmailFalso()


@pytest.fixture
def solicitar(usuarios, links, enviador, relogio):
    return SolicitarLinkMagico(
        usuarios=usuarios,
        links=links,
        enviador_email=enviador,
        relogio=relogio,
        url_base=URL_BASE,
    )


@pytest.fixture
def entrar(usuarios, links, relogio):
    return EntrarComLinkMagico(
        links=links,
        usuarios=usuarios,
        servico_token=ServicoTokenFalso(),
        relogio=relogio,
    )


def extrair_token(corpo):
    linha_link = next(
        linha for linha in corpo.splitlines() if linha.startswith(URL_BASE)
    )
    return parse_qs(urlparse(linha_link).query)["token"][0]


def test_ca6_envia_link_para_o_email_do_usuario(solicitar, enviador):
    solicitar.executar(EMAIL)

    [email] = enviador.enviados
    assert email.destinatario == EMAIL
    assert email.assunto == ASSUNTO_LINK_MAGICO
    assert "15 minutos" in email.corpo
    assert extrair_token(email.corpo)


def test_email_e_comparado_sem_diferenciar_maiusculas(solicitar, enviador):
    solicitar.executar("  ANA@Aluno.PUC-Rio.br ")

    assert len(enviador.enviados) == 1


def test_email_desconhecido_nao_envia_nada_nem_falha(solicitar, enviador):
    solicitar.executar("ninguem@puc-rio.br")

    assert enviador.enviados == []


def test_ca5_email_fora_dos_dominios_e_recusado(solicitar, enviador):
    with pytest.raises(EmailNaoInstitucional):
        solicitar.executar("ana@gmail.com")

    assert enviador.enviados == []


def test_terceirizado_nao_recebe_link(usuarios, solicitar, enviador):
    usuarios.adicionar(criar_usuario(vinculo=Vinculo.TERCEIRIZADO))

    solicitar.executar(EMAIL)

    assert enviador.enviados == []


def test_token_nao_e_guardado_em_texto_puro(solicitar, enviador, links):
    solicitar.executar(EMAIL)
    token = extrair_token(enviador.enviados[0].corpo)

    assert links.buscar_por_token_hash(token) is None


def test_ca6_link_valido_autentica_o_usuario(solicitar, entrar, enviador):
    solicitar.executar(EMAIL)

    sessao = entrar.executar(extrair_token(enviador.enviados[0].corpo))

    assert sessao.token == "token-1"


def test_ca7_link_so_pode_ser_usado_uma_vez(solicitar, entrar, enviador):
    solicitar.executar(EMAIL)
    token = extrair_token(enviador.enviados[0].corpo)
    entrar.executar(token)

    with pytest.raises(TokenInvalido):
        entrar.executar(token)


def test_ca7_link_expira_em_15_minutos(solicitar, entrar, enviador, relogio):
    solicitar.executar(EMAIL)
    relogio.avancar(timedelta(minutes=15))

    with pytest.raises(TokenInvalido):
        entrar.executar(extrair_token(enviador.enviados[0].corpo))


def test_ca7_token_desconhecido_e_recusado(entrar):
    with pytest.raises(TokenInvalido):
        entrar.executar("token-inventado")
