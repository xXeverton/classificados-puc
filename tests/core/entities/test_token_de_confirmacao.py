from datetime import UTC, datetime, timedelta

import pytest

from server.core.entities.token_de_confirmacao import TokenDeConfirmacao

AGORA = datetime(2026, 11, 20, 12, 0, tzinfo=UTC)


def criar_token(**overrides) -> TokenDeConfirmacao:
    dados = {
        "usuario_id": 1,
        "token_hash": "hash",
        "expira_em": AGORA + timedelta(minutes=15),
    }
    dados.update(overrides)
    return TokenDeConfirmacao(**dados)


def test_token_is_valid_until_expiration():
    token = criar_token()

    assert token.esta_valido(AGORA)
    assert token.esta_valido(AGORA + timedelta(minutes=15))


def test_token_expires_after_expiration():
    token = criar_token()
    depois = AGORA + timedelta(minutes=15, seconds=1)

    assert token.esta_expirado(depois)
    assert not token.esta_valido(depois)


def test_used_token_is_no_longer_valid():
    token = criar_token().usar(AGORA)

    assert token.usado_em == AGORA
    assert token.foi_usado()
    assert not token.esta_valido(AGORA)


def test_invalid_token_cannot_be_used():
    with pytest.raises(ValueError):
        criar_token().usar(AGORA).usar(AGORA)
