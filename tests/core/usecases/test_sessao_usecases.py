from datetime import timedelta

import pytest

from server.core.usecases.erros import SessaoInvalida
from tests.core.usecases.conftest import DURACAO_SESSAO, SENHA


def logar(ambiente) -> str:
    ambiente.cadastrar_confirmado()
    return ambiente.autenticar.executar("ana", SENHA).token


def test_active_session_returns_logged_user(ambiente):
    token = logar(ambiente)

    assert ambiente.obter_usuario.executar(token).nome_usuario == "ana"


def test_logout_revokes_session(ambiente):
    token = logar(ambiente)

    ambiente.encerrar.executar(token)

    with pytest.raises(SessaoInvalida):
        ambiente.obter_usuario.executar(token)
    with pytest.raises(SessaoInvalida):
        ambiente.encerrar.executar(token)


def test_expired_session_is_invalid(ambiente):
    token = logar(ambiente)
    ambiente.relogio.avancar(DURACAO_SESSAO)

    with pytest.raises(SessaoInvalida):
        ambiente.obter_usuario.executar(token)
    with pytest.raises(SessaoInvalida):
        ambiente.encerrar.executar(token)


def test_session_is_valid_just_before_expiration(ambiente):
    token = logar(ambiente)
    ambiente.relogio.avancar(DURACAO_SESSAO - timedelta(seconds=1))

    assert ambiente.obter_usuario.executar(token)


@pytest.mark.parametrize("token", ["inexistente", ""])
def test_unknown_session_is_invalid(ambiente, token):
    with pytest.raises(SessaoInvalida):
        ambiente.obter_usuario.executar(token)
    with pytest.raises(SessaoInvalida):
        ambiente.encerrar.executar(token)
