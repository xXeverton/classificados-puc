"""Representation of a newly opened session."""

from datetime import datetime

from pydantic import BaseModel

from server.core.usecases.autenticar import ResultadoAutenticacao


class SessaoViewSchema(BaseModel):
    token: str
    expira_em: datetime


def apresenta_sessao(resultado: ResultadoAutenticacao) -> SessaoViewSchema:
    return SessaoViewSchema(
        token=resultado.token, expira_em=resultado.expira_em
    )
