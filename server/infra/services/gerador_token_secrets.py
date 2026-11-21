"""Cryptographically secure token generation."""

import secrets

from server.core.interfaces.gerador_de_token_interface import (
    GeradorDeTokenInterface,
)

BYTES_DE_ENTROPIA = 32


class GeradorDeTokenSecrets(GeradorDeTokenInterface):

    def gerar(self) -> str:
        return secrets.token_urlsafe(BYTES_DE_ENTROPIA)
