from urllib.parse import parse_qs, urlparse

import pytest

from app.main import create_app
from infra.repositories.memoria import UsuarioRepositoryMemoria
from infra.seguranca.verificador_senha_werkzeug import (
    VerificadorSenhaWerkzeug,
)
from tests.fakes import EnviadorEmailFalso, criar_usuario

EMAIL = "ana@aluno.puc-rio.br"
MATRICULA = "2310001"
SENHA = "senha-correta"
URL_LINK = "https://classificados.puc/entrar/link"


@pytest.fixture
def enviador():
    return EnviadorEmailFalso()


@pytest.fixture
def cliente(enviador):
    senha_hash = VerificadorSenhaWerkzeug().gerar_hash(SENHA)
    app = create_app(
        {
            "TESTING": True,
            "JWT_SECRET": "segredo-de-teste-com-tamanho-suficiente",
            "URL_LINK_MAGICO": URL_LINK,
        },
        usuarios=UsuarioRepositoryMemoria(
            [criar_usuario(senha_hash=senha_hash)]
        ),
        enviador_email=enviador,
    )
    return app.test_client()


def entrar(cliente, senha=SENHA, email=EMAIL):
    return cliente.post("/auth/login", json={"email": email, "senha": senha})


def test_ca1_login_valido_retorna_token(cliente):
    resposta = entrar(cliente)

    assert resposta.status_code == 200
    corpo = resposta.get_json()
    assert corpo["token_type"] == "Bearer"
    assert corpo["expires_in"] == 3600
    assert corpo["access_token"]


def test_ca2_login_invalido_retorna_401_com_mensagem(cliente):
    resposta = entrar(cliente, senha="errada")

    assert resposta.status_code == 401
    assert resposta.get_json() == {"erro": "E-mail ou senha inválidos"}


@pytest.mark.parametrize(
    "corpo",
    [{}, {"email": EMAIL}, {"senha": SENHA},
     {"email": 123, "senha": SENHA}],
)
def test_login_sem_campos_validos_retorna_400(cliente, corpo):
    assert cliente.post("/auth/login", json=corpo).status_code == 400


def test_ca5_login_com_email_externo_retorna_400(cliente):
    resposta = entrar(cliente, email="ana@gmail.com")

    assert resposta.status_code == 400
    assert "e-mail institucional" in resposta.get_json()["erro"]


def test_ca3_quinto_erro_bloqueia_com_retry_after(cliente):
    for _ in range(5):
        entrar(cliente, senha="errada")

    resposta = entrar(cliente)

    assert resposta.status_code == 429
    assert 0 < int(resposta.headers["Retry-After"]) <= 600


def test_ca8_me_com_token_retorna_o_usuario(cliente):
    token = entrar(cliente).get_json()["access_token"]

    resposta = cliente.get(
        "/auth/me", headers={"Authorization": f"Bearer {token}"}
    )

    assert resposta.status_code == 200
    assert resposta.get_json()["matricula"] == MATRICULA
    assert resposta.get_json()["vinculo"] == "aluno"


@pytest.mark.parametrize(
    "cabecalhos",
    [{}, {"Authorization": "Bearer invalido"}, {"Authorization": "Basic x"}],
)
def test_ca8_me_sem_token_valido_retorna_401(cliente, cabecalhos):
    assert cliente.get("/auth/me", headers=cabecalhos).status_code == 401


def test_link_magico_responde_igual_para_email_existente_ou_nao(
    cliente, enviador
):
    existente = cliente.post(
        "/auth/link-magico", json={"email": "ana@aluno.puc-rio.br"}
    )
    inexistente = cliente.post(
        "/auth/link-magico", json={"email": "ninguem@puc-rio.br"}
    )

    assert existente.status_code == inexistente.status_code == 202
    assert existente.get_json() == inexistente.get_json()
    assert len(enviador.enviados) == 1


def test_link_magico_sem_email_retorna_400(cliente):
    assert cliente.post("/auth/link-magico", json={}).status_code == 400


def test_ca5_link_magico_com_email_externo_retorna_400(cliente, enviador):
    resposta = cliente.post(
        "/auth/link-magico", json={"email": "ana@gmail.com"}
    )

    assert resposta.status_code == 400
    assert "@aluno.puc-rio.br" in resposta.get_json()["erro"]
    assert enviador.enviados == []


def test_ca6_ca7_link_magico_autentica_uma_unica_vez(cliente, enviador):
    cliente.post("/auth/link-magico", json={"email": "ana@aluno.puc-rio.br"})
    linha_link = next(
        linha
        for linha in enviador.enviados[0].corpo.splitlines()
        if linha.startswith(URL_LINK)
    )
    token = parse_qs(urlparse(linha_link).query)["token"][0]

    primeira = cliente.post("/auth/link-magico/validar", json={"token": token})
    segunda = cliente.post("/auth/link-magico/validar", json={"token": token})

    assert primeira.status_code == 200
    assert primeira.get_json()["access_token"]
    assert segunda.status_code == 401


def test_falha_no_envio_do_email_retorna_503(cliente, enviador):
    from use_cases.autenticacao.portas import FalhaEnvioEmail

    def enviar_com_falha(*args, **kwargs):
        raise FalhaEnvioEmail("smtp fora do ar")

    enviador.enviar = enviar_com_falha

    resposta = cliente.post(
        "/auth/link-magico", json={"email": "ana@aluno.puc-rio.br"}
    )

    assert resposta.status_code == 503
