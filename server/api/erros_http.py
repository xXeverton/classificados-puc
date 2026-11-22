"""Translate use case errors into HTTP responses at the API boundary."""

from flask import Flask, Response, current_app, jsonify, request
from pydantic import ValidationError
from werkzeug.exceptions import HTTPException, RequestEntityTooLarge

from server.api.presenters.error_presenter import (
    apresenta_erro,
    apresenta_erro_de_validacao,
)
from server.core.usecases.erros import (
    ContaBloqueada,
    AnuncioExcluido,
    AnuncioExpirado,
    AnuncioNaoEncontrado,
    AnuncioNaoPublicado,
    AnuncioVendido,
    CredenciaisInvalidas,
    DadosInvalidos,
    EmailEmUso,
    EmailNaoConfirmado,
    ErroDeCasoDeUso,
    FotoInvalida,
    IdentificadorEmUso,
    PerfilIncompleto,
    PerfilNaoEncontrado,
    SessaoInvalida,
    TokenExpirado,
    TokenInvalido,
    UsuarioNaoAutenticado,
)

STATUS_DE_VALIDACAO = 400
STATUS_ARQUIVO_GRANDE = 413
MENSAGEM_ARQUIVO_GRANDE = "O envio excede o limite permitido."

_STATUS_POR_ERRO: dict[type[ErroDeCasoDeUso], int] = {
    AnuncioExcluido: 404,
    AnuncioExpirado: 404,
    AnuncioNaoEncontrado: 404,
    AnuncioNaoPublicado: 404,
    AnuncioVendido: 404,
    DadosInvalidos: 400,
    FotoInvalida: 400,
    PerfilNaoEncontrado: 404,
    TokenInvalido: 400,
    CredenciaisInvalidas: 401,
    SessaoInvalida: 401,
    EmailNaoConfirmado: 403,
    PerfilIncompleto: 403,
    EmailEmUso: 409,
    IdentificadorEmUso: 409,
    TokenExpirado: 410,
    ContaBloqueada: 429,
    UsuarioNaoAutenticado: 401,
}

_CODIGO_POR_ERRO: dict[type[ErroDeCasoDeUso], str] = {
    EmailNaoConfirmado: "email_nao_confirmado",
    DadosInvalidos: "dados_invalidos",
    PerfilIncompleto: "perfil_incompleto",
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


def resposta_de_erro_http(erro: HTTPException) -> Response:
    """Keep framework HTTP errors under /api/ in the public JSON format."""
    if not request.path.startswith("/api/"):
        return erro.get_response()

    mensagem = {
        400: "Requisição inválida.",
        404: "Rota da API não encontrada.",
        405: "Método não permitido para esta rota.",
        415: "Tipo de conteúdo não suportado.",
    }.get(erro.code, "Requisição inválida.")
    resposta = jsonify(apresenta_erro(mensagem).model_dump(exclude_none=True))
    resposta.status_code = erro.code or 500
    return resposta


def resposta_de_erro_inesperado(erro: Exception) -> Response:
    """Return a generic JSON 500 for unexpected API failures."""
    if not request.path.startswith("/api/"):
        return current_app.handle_exception(erro)

    current_app.logger.exception("Falha inesperada em rota da API.")
    resposta = jsonify(
        apresenta_erro("Erro interno ao processar a requisição.").model_dump(
            exclude_none=True
        )
    )
    resposta.status_code = 500
    return resposta


def registrar_tratamento_de_erros(app: Flask) -> None:
    app.register_error_handler(ErroDeCasoDeUso, resposta_de_erro)
    app.register_error_handler(
        RequestEntityTooLarge, resposta_de_arquivo_grande
    )
    app.register_error_handler(HTTPException, resposta_de_erro_http)
    app.register_error_handler(Exception, resposta_de_erro_inesperado)
