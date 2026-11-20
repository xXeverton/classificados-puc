from datetime import UTC, datetime, timedelta

import pytest

from server.core.entities.usuario import Usuario
from server.core.entities.vinculo import Vinculo

AGORA = datetime(2026, 11, 20, 12, 0, tzinfo=UTC)


def criar_usuario(**overrides) -> Usuario:
    dados = {
        "nome": "Ana",
        "email": "ana@aluno.puc-rio.br",
        "nome_usuario": "ana",
        "matricula": "123",
        "vinculo": Vinculo.ALUNO,
        "senha_hash": "hash",
    }
    dados.update(overrides)
    return Usuario(**dados)


@pytest.mark.parametrize(
    "email",
    [
        "ana@aluno.puc-rio.br",
        "ana.silva+teste@aluno.puc-rio.br",
        "funcionario@puc-rio.br",
    ],
)
def test_usuario_accepts_valid_institutional_emails(email):
    assert criar_usuario(email=email).email == email


@pytest.mark.parametrize(
    "email",
    [
        "",
        "@aluno.puc-rio.br",
        "ana..silva@aluno.puc-rio.br",
        "ana@sub.aluno.puc-rio.br",
        "ana@aluno.puc-rio.br.example.com",
        "ana@gmail.com",
        "ana @puc-rio.br",
    ],
)
def test_usuario_rejects_invalid_or_non_institutional_emails(email):
    with pytest.raises(ValueError):
        criar_usuario(email=email)


def test_usuario_normalizes_email_username_and_matricula():
    usuario = criar_usuario(
        email="  ANA@ALUNO.PUC-RIO.BR ",
        nome_usuario=" Ana.Silva ",
        matricula=" ABC123 ",
    )

    assert usuario.email == "ana@aluno.puc-rio.br"
    assert usuario.nome_usuario == "ana.silva"
    assert usuario.matricula == "abc123"


@pytest.mark.parametrize("nome", ["", "   "])
def test_usuario_requires_nome(nome):
    with pytest.raises(ValueError, match="Nome"):
        criar_usuario(nome=nome)


@pytest.mark.parametrize("nome_usuario", ["", "  "])
def test_usuario_requires_nome_usuario(nome_usuario):
    with pytest.raises(ValueError, match="Nome de usuário"):
        criar_usuario(nome_usuario=nome_usuario)


def test_usuario_rejects_nome_usuario_with_at_sign():
    with pytest.raises(ValueError, match="@"):
        criar_usuario(nome_usuario="ana@puc")


@pytest.mark.parametrize("matricula", [None, "", "   "])
def test_usuario_matricula_is_optional(matricula):
    assert criar_usuario(matricula=matricula).matricula is None


@pytest.mark.parametrize(
    ("valor", "esperado"),
    [
        ("aluno", Vinculo.ALUNO),
        ("funcionario", Vinculo.FUNCIONARIO),
        (Vinculo.FUNCIONARIO, Vinculo.FUNCIONARIO),
    ],
)
def test_usuario_accepts_known_vinculos(valor, esperado):
    assert criar_usuario(vinculo=valor).vinculo is esperado


@pytest.mark.parametrize("vinculo", ["", "terceirizado", "professor"])
def test_usuario_rejects_unknown_vinculo(vinculo):
    with pytest.raises(ValueError, match="Vínculo"):
        criar_usuario(vinculo=vinculo)


def test_usuario_requires_senha_hash():
    with pytest.raises(ValueError):
        criar_usuario(senha_hash="")


def test_new_usuario_is_pending_until_confirmed():
    usuario = criar_usuario()

    assert not usuario.esta_confirmado()
    confirmado = usuario.confirmar(AGORA)
    assert confirmado.esta_confirmado()
    assert confirmado.confirmado_em == AGORA
    assert not usuario.esta_confirmado()


def test_four_failed_logins_do_not_lock_the_account():
    usuario = criar_usuario()
    for _ in range(4):
        usuario = usuario.registrar_falha_de_login(AGORA)

    assert usuario.tentativas_login_falhas == 4
    assert not usuario.esta_bloqueado(AGORA)


def test_fifth_failed_login_locks_for_ten_minutes_and_resets_count():
    usuario = criar_usuario()
    for _ in range(5):
        usuario = usuario.registrar_falha_de_login(AGORA)

    assert usuario.tentativas_login_falhas == 0
    assert usuario.bloqueado_ate == AGORA + timedelta(minutes=10)
    assert usuario.esta_bloqueado(AGORA + timedelta(minutes=9, seconds=59))
    assert not usuario.esta_bloqueado(AGORA + timedelta(minutes=10))


def test_successful_login_resets_failed_attempts():
    usuario = criar_usuario().registrar_falha_de_login(AGORA)

    usuario = usuario.registrar_login_bem_sucedido()

    assert usuario.tentativas_login_falhas == 0
    assert usuario.bloqueado_ate is None
