"""Translate use case errors into HTTP responses at the API boundary."""

from flask import Flask, Response, jsonify
from pydantic import ValidationError
from werkzeug.exceptions import RequestEntityTooLarge

from server.api.presenters.error_presenter import (
    apresenta_erro,
    apresenta_erro_de_validacao,
)
from server.core.usecases.erros import (
    ContaBloqueada,
    CredenciaisInvalidas,
    DadosInvalidos,
    EmailEmUso,
    EmailNaoConfirmado,
    ErroDeCasoDeUso,
    FotoInvalida,
    IdentificadorEmUso,
    PerfilNaoEncontrado,
    SessaoInvalida,
    TokenExpirado,
    TokenInvalido,
)

STATUS_DE_VALIDACAO = 400
STATUS_ARQUIVO_GRANDE = 413
MENSAGEM_ARQUIVO_GRANDE = (
    "O envio é grande demais. A foto deve ter no máximo 2 MB."
)

_STATUS_POR_ERRO: dict[type[ErroDeCasoDeUso], int] = {
    DadosInvalidos: 400,
    FotoInvalida: 400,
    PerfilNaoEncontrado: 404,
    TokenInvalido: 400,
    CredenciaisInvalidas: 401,
    SessaoInvalida: 401,
    EmailNaoConfirmado: 403,
    EmailEmUso: 409,
    IdentificadorEmUso: 409,
    TokenExpirado: 410,
    ContaBloqueada: 429,
}

_CODIGO_POR_ERRO: dict[type[ErroDeCasoDeUso], str] = {
    EmailNaoConfirmado: "email_nao_confirmado",
    DadosInvalidos: "dados_invalidos",
    FotoInvalida: "foto_invalida",
    PerfilNaoEncontrado: "perfil_nao_encontrado",
}


def resposta_de_erro(erro: ErroDeCasoDeUso) -> tuple[dict, int]:
    """Return the JSON body and status for a known use case error."""
    status = _STATUS_POR_ERRO.get(type(erro))
    if status is None:
        raise erro
    corpo = apresenta_erro(erro.mensagem, _CODIGO_POR_ERRO.get(type(erro)))
    return corpo.model_dump(exclude_none=True), status


def resposta_de_validacao(erro: ValidationError) -> Response:
    """flask-openapi3 callback: invalid request bodies answer 400."""
    corpo = apresenta_erro_de_validacao(erro)
    resposta = jsonify(corpo.model_dump(exclude_none=True))
    resposta.status_code = STATUS_DE_VALIDACAO
    return resposta


def resposta_de_arquivo_grande(
    _erro: RequestEntityTooLarge,
) -> tuple[dict, int]:
    """Flask answers 413 when the request body exceeds the limit."""
    corpo = apresenta_erro(MENSAGEM_ARQUIVO_GRANDE, "arquivo_grande")
    return corpo.model_dump(exclude_none=True), STATUS_ARQUIVO_GRANDE


def registrar_tratamento_de_erros(app: Flask) -> None:
    app.register_error_handler(ErroDeCasoDeUso, resposta_de_erro)
    app.register_error_handler(
        RequestEntityTooLarge, resposta_de_arquivo_grande
    )
