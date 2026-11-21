"""Route protection: every content route must require a valid session."""

from collections.abc import Callable
from functools import wraps

from flask import g, request

from server.core.usecases.erros import SessaoInvalida
from server.core.usecases.obter_usuario_da_sessao import (
    ObterUsuarioDaSessao,
)

ESQUEMA_DE_SEGURANCA = "bearer"
SEGURANCA_BEARER = [{ESQUEMA_DE_SEGURANCA: []}]
_PREFIXO_BEARER = "bearer "


def token_da_requisicao() -> str | None:
    """Return the token from `Authorization: Bearer <token>`, if present."""
    cabecalho = request.headers.get("Authorization", "")
    if not cabecalho.lower().startswith(_PREFIXO_BEARER):
        return None
    token = cabecalho[len(_PREFIXO_BEARER):].strip()
    return token or None


def exige_sessao(
    obter_usuario_da_sessao: ObterUsuarioDaSessao,
) -> Callable[[Callable], Callable]:
    """Build a decorator that answers 401 without a valid session.

    The logged-in user is available to the view as `flask.g.usuario`.
    """

    def decorador(view: Callable) -> Callable:
        @wraps(view)
        def protegida(*args, **kwargs):
            token = token_da_requisicao()
            if token is None:
                raise SessaoInvalida()
            g.usuario = obter_usuario_da_sessao.executar(token)
            g.token_sessao = token
            return view(*args, **kwargs)

        return protegida

    return decorador
