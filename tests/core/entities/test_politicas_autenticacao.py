import hashlib
from datetime import timedelta

from server.core.entities import politicas_autenticacao as politicas


def test_authentication_policy_values():
    assert politicas.VALIDADE_TOKEN_CONFIRMACAO == timedelta(minutes=15)
    assert politicas.MAXIMO_TENTATIVAS_LOGIN == 5
    assert politicas.DURACAO_BLOQUEIO_LOGIN == timedelta(minutes=10)


def test_hash_de_token_is_sha256_hex_and_differs_from_token():
    token_hash = politicas.hash_de_token("segredo")

    assert token_hash == hashlib.sha256(b"segredo").hexdigest()
    assert token_hash != "segredo"
