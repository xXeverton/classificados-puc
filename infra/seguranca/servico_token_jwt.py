"""Emissão e validação de tokens de sessão JWT (HS256)."""

from datetime import timedelta

import jwt

from domain.erros import TokenInvalido
from use_cases.autenticacao.portas import Relogio, SessaoAutenticada

_ALGORITMO = "HS256"
_TIPO_ACESSO = "acesso"


class ServicoTokenJwt:
    def __init__(
        self, segredo: str, validade: timedelta, relogio: Relogio
    ) -> None:
        if not segredo:
            raise ValueError("O segredo do JWT não pode ser vazio.")
        self._segredo = segredo
        self._validade = validade
        self._relogio = relogio

    def emitir(self, usuario_id: int) -> SessaoAutenticada:
        agora = self._relogio.agora()
        payload = {
            "sub": str(usuario_id),
            "tipo": _TIPO_ACESSO,
            "iat": agora,
            "exp": agora + self._validade,
        }
        token = jwt.encode(payload, self._segredo, algorithm=_ALGORITMO)
        return SessaoAutenticada(
            token=token,
            expira_em_segundos=int(self._validade.total_seconds()),
        )

    def validar(self, token: str) -> int:
        try:
            payload = jwt.decode(
                token,
                self._segredo,
                algorithms=[_ALGORITMO],
                options={"require": ["sub", "exp", "iat"]},
            )
            if payload.get("tipo") != _TIPO_ACESSO:
                raise TokenInvalido()
            return int(payload["sub"])
        except (jwt.PyJWTError, ValueError) as erro:
            raise TokenInvalido() from erro
