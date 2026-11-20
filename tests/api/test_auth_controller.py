from datetime import timedelta

import pytest

from server.app import create_app
from tests.core.usecases.fakes import (
    EnviadorDeEmailFalso,
    GeradorDeTokenFalso,
    RelogioFalso,
)

SENHA = "senha-segura"
CADASTRO = {
    "nome": "Ana",
    "email": "ana@aluno.puc-rio.br",
    "nome_usuario": "ana",
    "matricula": "2310001",
    "vinculo": "aluno",
    "senha": SENHA,
}


class Api:
    def __init__(self, app, client, relogio, enviador):
        self.app = app
        self.client = client
        self.relogio = relogio
        self.enviador = enviador

    def cadastrar(self, **overrides):
        return self.client.post(
            "/auth/cadastro", json={**CADASTRO, **overrides}
        )

    def confirmar(self, token=None):
        token = token or self.enviador.ultimo.token
        return self.client.post("/auth/confirmacao", json={"token": token})

    def login(self, identificador="ana", senha=SENHA):
        return self.client.post(
            "/auth/login",
            json={"identificador": identificador, "senha": senha},
        )

    def logar(self) -> str:
        self.cadastrar()
        self.confirmar()
        return self.login().json["token"]


@pytest.fixture
def api():
    relogio = RelogioFalso()
    enviador = EnviadorDeEmailFalso()
    app = create_app(
        {
            "DATABASE_URL": "sqlite:///:memory:",
            "RELOGIO": relogio,
            "ENVIADOR_EMAIL": enviador,
            "GERADOR_TOKEN": GeradorDeTokenFalso(),
            "CONFIRMACAO_URL_BASE": "http://front.example/confirmar",
        }
    )
    yield Api(app, app.test_client(), relogio, enviador)
    app.extensions["database_engine"].dispose()


def bearer(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_full_flow_register_confirm_login_me_logout(api):
    cadastro = api.cadastrar()
    assert cadastro.status_code == 201
    assert cadastro.json == {
        "id": cadastro.json["id"],
        "nome": "Ana",
        "email": "ana@aluno.puc-rio.br",
        "nome_usuario": "ana",
        "matricula": "2310001",
        "vinculo": "aluno",
        "email_confirmado": False,
    }
    assert "senha_hash" not in cadastro.json
    assert api.enviador.ultimo.corpo.count(
        "http://front.example/confirmar?token="
    ) == 1

    confirmacao = api.confirmar()
    assert confirmacao.status_code == 200
    assert confirmacao.json["email_confirmado"] is True

    login = api.login("ana@aluno.puc-rio.br")
    assert login.status_code == 200
    assert set(login.json) == {"token", "expira_em"}
    token = login.json["token"]

    me = api.client.get("/auth/me", headers=bearer(token))
    assert me.status_code == 200
    assert me.json["nome_usuario"] == "ana"

    logout = api.client.post("/auth/logout", headers=bearer(token))
    assert logout.status_code == 204

    depois = api.client.get("/auth/me", headers=bearer(token))
    assert depois.status_code == 401


@pytest.mark.parametrize(
    ("overrides", "trecho"),
    [
        ({"email": "ana@gmail.com"}, "institucionais"),
        ({"senha": "1234567"}, "8 caracteres"),
        ({"nome": " "}, "Nome"),
        ({"vinculo": "terceirizado"}, "Vínculo"),
        ({"nome_usuario": "ana@x"}, "@"),
    ],
)
def test_cadastro_with_invalid_data_returns_400(api, overrides, trecho):
    response = api.cadastrar(**overrides)

    assert response.status_code == 400
    assert trecho in response.json["message"]


@pytest.mark.parametrize("campo", ["nome", "vinculo", "senha"])
def test_cadastro_missing_field_returns_400(api, campo):
    corpo = {k: v for k, v in CADASTRO.items() if k != campo}

    response = api.client.post("/auth/cadastro", json=corpo)

    assert response.status_code == 400
    assert campo in response.json["message"]


def test_cadastro_without_matricula_returns_201(api):
    corpo = {k: v for k, v in CADASTRO.items() if k != "matricula"}

    response = api.client.post("/auth/cadastro", json=corpo)

    assert response.status_code == 201
    assert response.json["matricula"] is None


def test_cadastro_with_identifiers_in_use_returns_409(api):
    api.cadastrar()
    api.confirmar()

    email = api.cadastrar()
    nome_usuario = api.cadastrar(email="bia@aluno.puc-rio.br", matricula="9")

    assert email.status_code == 409
    assert email.json["message"] == "E-mail já está em uso."
    assert nome_usuario.status_code == 409
    assert "Nome de usuário" in nome_usuario.json["message"]


def test_confirmacao_with_used_or_unknown_token_returns_400(api):
    api.cadastrar()
    token = api.enviador.ultimo.token
    api.confirmar(token)

    assert api.confirmar(token).status_code == 400
    assert api.confirmar("inexistente").status_code == 400


def test_confirmacao_with_expired_token_returns_410(api):
    api.cadastrar()
    api.relogio.avancar(timedelta(minutes=15, seconds=1))

    response = api.confirmar()

    assert response.status_code == 410
    assert "expirado" in response.json["message"]


@pytest.mark.parametrize(
    "email", ["ana@aluno.puc-rio.br", "ninguem@aluno.puc-rio.br"]
)
def test_reenviar_always_returns_202_with_generic_message(api, email):
    api.cadastrar()

    response = api.client.post(
        "/auth/confirmacao/reenviar", json={"email": email}
    )

    assert response.status_code == 202
    assert "Se houver um cadastro pendente" in response.json["message"]


def test_reenviar_sends_new_link_to_pending_account(api):
    api.cadastrar()
    antigo = api.enviador.ultimo.token

    api.client.post(
        "/auth/confirmacao/reenviar", json={"email": "ana@aluno.puc-rio.br"}
    )

    assert api.confirmar(antigo).status_code == 400
    assert api.confirmar().status_code == 200


def test_login_with_wrong_credentials_returns_401(api):
    api.cadastrar()
    api.confirmar()

    for identificador, senha in [("ana", "errada!!"), ("ninguem", SENHA)]:
        response = api.login(identificador, senha)
        assert response.status_code == 401
        assert response.json == {"message": "Credenciais inválidas"}


def test_login_of_pending_account_returns_403_with_code(api):
    api.cadastrar()

    response = api.login("2310001")

    assert response.status_code == 403
    assert response.json["code"] == "email_nao_confirmado"


def test_login_of_locked_account_returns_429(api):
    api.cadastrar()
    api.confirmar()
    for _ in range(5):
        api.login(senha="errada!!")

    response = api.login("ana@aluno.puc-rio.br")

    assert response.status_code == 429


@pytest.mark.parametrize(
    "headers",
    [{}, {"Authorization": "Bearer "}, {"Authorization": "Basic abc"},
     bearer("inexistente")],
)
def test_protected_routes_without_valid_session_return_401(api, headers):
    me = api.client.get("/auth/me", headers=headers)
    logout = api.client.post("/auth/logout", headers=headers)

    assert me.status_code == 401
    assert logout.status_code == 401
    assert me.json["message"] == "Sessão inválida ou expirada."


def test_expired_session_returns_401(api):
    token = api.logar()
    api.relogio.avancar(timedelta(hours=8))

    assert api.client.get("/auth/me", headers=bearer(token)).status_code == (
        401
    )


def test_smtp_backend_without_configuration_fails_clearly():
    with pytest.raises(ValueError, match="SMTP_HOST"):
        create_app(
            {"DATABASE_URL": "sqlite:///:memory:", "EMAIL_BACKEND": "smtp"}
        )


def test_unknown_email_backend_fails_clearly():
    with pytest.raises(ValueError, match="EMAIL_BACKEND"):
        create_app(
            {"DATABASE_URL": "sqlite:///:memory:", "EMAIL_BACKEND": "x"}
        )


def test_smtp_backend_with_configuration_starts():
    app = create_app(
        {
            "DATABASE_URL": "sqlite:///:memory:",
            "EMAIL_BACKEND": "smtp",
            "SMTP_HOST": "smtp.example",
            "SMTP_PORT": "587",
            "SMTP_USUARIO": "user",
            "SMTP_SENHA": "secret",
            "EMAIL_REMETENTE": "noreply@example.com",
        }
    )
    app.extensions["database_engine"].dispose()


def test_openapi_documents_auth_routes(api):
    paths = api.client.get("/openapi/openapi.json").json["paths"]

    assert {
        "/auth/cadastro", "/auth/confirmacao", "/auth/confirmacao/reenviar",
        "/auth/login", "/auth/logout", "/auth/me",
    } <= set(paths)
