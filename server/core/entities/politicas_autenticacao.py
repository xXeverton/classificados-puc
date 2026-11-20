"""Authentication policies shared by entities and use cases."""

import hashlib
from datetime import timedelta

VALIDADE_TOKEN_CONFIRMACAO = timedelta(minutes=15)
MAXIMO_TENTATIVAS_LOGIN = 5
DURACAO_BLOQUEIO_LOGIN = timedelta(minutes=10)


def hash_de_token(token: str) -> str:
    """Return the SHA-256 hex digest stored in place of a secret token."""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()
