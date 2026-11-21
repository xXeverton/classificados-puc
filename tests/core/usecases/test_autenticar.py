from datetime import timedelta

import pytest

from server.core.entities.politicas_autenticacao import hash_de_token
from server.core.usecases.erros import (
    ContaBloqueada,
    CredenciaisInvalidas,
    EmailNaoConfirmado,
)
from tests.core.usecases.conftest import DURACAO_SESSAO, SENHA


@pytest.mark.parametrize(
    "identificador",
    ["ana@aluno.puc-rio.br", " ANA@Aluno.PUC-Rio.br", "ana", "ANA", "2310001"],
)
def test_confirmed_account_logs_in_with_any_identifier(
    ambiente, identificador
):
    usuario = ambiente.cadastrar_confirmado()

    resultado = ambiente.autenticar.executar(identificador, SENHA)

    assert resultado.expira_em == ambiente.relogio.agora() + DURACAO_SESSAO
    sessao = ambiente.sessoes.buscar_por_hash(hash_de_token(resultado.token))
    assert sessao.usuario_id == usuario.id
    assert ambiente.obter_usuario.executar(resultado.token).id == usuario.id


@pytest.mark.parametrize("identificador", ["ana@aluno.puc-rio.br", "ana"])
def test_pending_account_with_right_password_must_confirm_email(
    ambiente, identificador
):
    ambiente.cadastrar_ana()

    with pytest.raises(EmailNaoConfirmado):
        ambiente.autenticar.executar(identificador, SENHA)

    assert ambiente.sessoes.sessoes == {}


def test_pending_account_with_wrong_password_gets_invalid_credentials(
    ambiente,
):
    ambiente.cadastrar_ana()

    with pytest.raises(CredenciaisInvalidas):
        ambiente.autenticar.executar("ana", "senha-errada")


@pytest.mark.parametrize(
    ("identificador", "senha"),
    [
        ("ninguem@aluno.puc-rio.br", SENHA),
        ("ninguem", SENHA),
        ("", SENHA),
        ("ana", "senha-errada"),
    ],
)
def test_unknown_identifier_and_wrong_password_give_same_error(
    ambiente, identificador, senha
):
    ambiente.cadastrar_confirmado()

    with pytest.raises(CredenciaisInvalidas) as erro:
        ambiente.autenticar.executar(identificador, senha)

    assert str(erro.value) == "Credenciais inválidas"


def errar_senha(ambiente, vezes, identificadores=("ana",)):
    for tentativa in range(vezes):
        identificador = identificadores[tentativa % len(identificadores)]
        with pytest.raises(CredenciaisInvalidas):
            ambiente.autenticar.executar(identificador, "senha-errada")


def test_five_wrong_passwords_lock_account_for_any_identifier(ambiente):
    ambiente.cadastrar_confirmado()
    errar_senha(
        ambiente, 5,
        identificadores=("ana", "2310001", "ana@aluno.puc-rio.br"),
    )

    for identificador in ("ana", "2310001", "ana@aluno.puc-rio.br"):
        with pytest.raises(ContaBloqueada):
            ambiente.autenticar.executar(identificador, SENHA)


def test_attempts_during_lock_do_not_count_and_login_returns_after_10_min(
    ambiente,
):
    ambiente.cadastrar_confirmado()
    errar_senha(ambiente, 5)
    ambiente.relogio.avancar(timedelta(minutes=9, seconds=59))
    with pytest.raises(ContaBloqueada):
        ambiente.autenticar.executar("ana", "senha-errada")

    ambiente.relogio.avancar(timedelta(seconds=1))

    assert ambiente.autenticar.executar("ana", SENHA).token


def test_lock_after_expiration_starts_a_fresh_count(ambiente):
    ambiente.cadastrar_confirmado()
    errar_senha(ambiente, 5)
    ambiente.relogio.avancar(timedelta(minutes=10))

    errar_senha(ambiente, 4)

    assert ambiente.autenticar.executar("ana", SENHA).token


def test_successful_login_resets_failed_attempts(ambiente):
    ambiente.cadastrar_confirmado()
    errar_senha(ambiente, 4)

    ambiente.autenticar.executar("ana", SENHA)
    errar_senha(ambiente, 4)

    assert ambiente.autenticar.executar("ana", SENHA).token
