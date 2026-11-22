"""HTTP controllers for publishing and browsing advertisements."""

import json
import re
from dataclasses import replace
from decimal import Decimal, InvalidOperation
from http import HTTPStatus
from typing import Any, NoReturn

from flask import current_app, g, request
from flask_openapi3 import OpenAPI

from werkzeug.datastructures import FileStorage

from server.api.autenticacao import SEGURANCA_BEARER, exige_sessao
from server.api.presenters.ad_presenter import (
    AdViewSchema,
    AdsFeedViewSchema,
    apresenta_ad,
    apresenta_feed,
)
from server.api.presenters.error_presenter import (
    ErrorSchema,
    apresenta_erro,
)
from server.core.entities.anuncio import (
    Anuncio,
    DESCRICAO_MAX_CARACTERES,
    PRECO_MAXIMO,
    TITULO_MAX_CARACTERES,
    TITULO_MIN_CARACTERES,
)
from server.core.usecases.erros import ErroDeCasoDeUso, PerfilIncompleto
from server.core.usecases.list_ads import ListAds
from server.infra.storage.storage import (
    ChaveInvalidaError,
    ImageStorage,
    ImagemInvalidaError,
    StorageIndisponivelError,
)

_PADRAO_PRECO = re.compile(r"[0-9]+(?:[,.][0-9]{1,2})?")
_CAMPOS_PERMITIDOS = {
    "titulo",
    "categoria",
    "estado_conservacao",
    "descricao",
    "preco",
    "preco_a_combinar",
}


class ErroPublicacaoSchema(ErrorSchema):
    campos: dict[str, str] | None = None


def _rejeitar_constante_json(valor: str) -> NoReturn:
    raise ValueError(f"Constante JSON não permitida: {valor}")


def _erro(
    mensagem: str,
    status: HTTPStatus,
    *,
    codigo: str | None = None,
    campos: dict[str, str] | None = None,
) -> tuple[dict[str, Any], int]:
    resposta = apresenta_erro(mensagem, codigo).model_dump(exclude_none=True)
    if campos is not None:
        resposta["campos"] = campos
    return resposta, status


def _preco_decimal(valor: Any) -> Decimal | None:
    if isinstance(valor, bool):
        return None
    if isinstance(valor, Decimal):
        preco = valor
    elif isinstance(valor, int):
        preco = Decimal(valor)
    elif isinstance(valor, str) and _PADRAO_PRECO.fullmatch(valor):
        try:
            preco = Decimal(valor.replace(",", "."))
        except InvalidOperation:
            return None
    else:
        return None
    if (
        not preco.is_finite()
        or preco < 0
        or preco > PRECO_MAXIMO
        or preco.as_tuple().exponent < -2
    ):
        return None
    return preco


def _ler_entrada() -> tuple[dict[str, Any] | None, FileStorage | None]:
    if request.mimetype == "application/json":
        try:
            dados = json.loads(
                request.get_data(cache=False),
                parse_float=Decimal,
                parse_constant=_rejeitar_constante_json,
            )
        except (UnicodeDecodeError, ValueError):
            return None, None
        return (dados if isinstance(dados, dict) else None), None

    if request.mimetype == "multipart/form-data":
        dados: dict[str, Any] = request.form.to_dict()
        imagem = request.files.get("imagem")
        if imagem is not None and not imagem.filename:
            imagem = None
        return dados, imagem

    return None, None


def _validar_anuncio(
    dados: dict[str, Any], usuario_id: int
) -> tuple[Anuncio | None, dict[str, str]]:
    erros = {
        campo: "Este campo não é permitido."
        for campo in sorted(set(dados) - _CAMPOS_PERMITIDOS)
    }

    titulo_raw = dados.get("titulo")
    titulo = titulo_raw.strip() if isinstance(titulo_raw, str) else ""
    if not TITULO_MIN_CARACTERES <= len(titulo) <= TITULO_MAX_CARACTERES:
        erros["titulo"] = "O título deve ter entre 5 e 80 caracteres."

    categoria = dados.get("categoria")
    if not isinstance(categoria, str) or categoria not in {
        "produto",
        "servico",
        "evento",
    }:
        erros["categoria"] = "Escolha produto, serviço ou evento."
        categoria = ""

    estado_raw = dados.get("estado_conservacao")
    estado = (
        estado_raw
        if isinstance(estado_raw, str) and estado_raw
        else None
    )
    if categoria == "produto":
        if estado not in {"novo", "usado_regular"}:
            erros["estado_conservacao"] = (
                "Informe o estado de conservação do produto."
            )
    elif estado_raw not in (None, ""):
        erros["estado_conservacao"] = (
            "Estado de conservação não se aplica a serviço ou evento."
        )

    descricao_raw = dados.get("descricao")
    descricao = descricao_raw.strip() if isinstance(descricao_raw, str) else ""
    if not descricao or len(descricao) > DESCRICAO_MAX_CARACTERES:
        erros["descricao"] = (
            "Informe uma descrição não vazia de até 500 caracteres."
        )

    combinar_raw = dados.get("preco_a_combinar", False)
    if isinstance(combinar_raw, str):
        if combinar_raw.lower() in {"true", "1", "on"}:
            combinar = True
        elif combinar_raw.lower() in {"false", "0", "off", ""}:
            combinar = False
        else:
            combinar = False
            erros["preco_a_combinar"] = "Informe uma opção válida."
    elif isinstance(combinar_raw, bool):
        combinar = combinar_raw
    else:
        combinar = False
        erros["preco_a_combinar"] = "Informe uma opção válida."

    preco = None
    preco_raw = dados.get("preco")
    if combinar:
        if preco_raw not in (None, ""):
            erros["preco"] = (
                "Não informe preço quando selecionar 'A combinar'."
            )
    else:
        preco = _preco_decimal(preco_raw)
        if preco is None:
            erros["preco"] = (
                "Informe um preço entre 0 e 9999999999,99, "
                "com até duas casas decimais."
            )

    if erros:
        return None, erros

    try:
        return (
            Anuncio(
                usuario_id=usuario_id,
                titulo=titulo,
                descricao=descricao,
                categoria=categoria,
                estado_conservacao=estado,
                preco=preco,
            ),
            {},
        )
    except ValueError as error:
        return None, {"anuncio": str(error)}


def _limpar_imagem(storage: ImageStorage, key: str | None) -> None:
    if key is None:
        return
    try:
        storage.remover(key)
    except (ChaveInvalidaError, StorageIndisponivelError):
        current_app.logger.exception(
            "Não foi possível remover imagem órfã do anúncio."
        )


def register_ads_controller(app: OpenAPI, obter_usuario_da_sessao) -> None:
    """Register authenticated feed and publication endpoints."""
    protegida = exige_sessao(obter_usuario_da_sessao)

    @app.get(
        "/api/ads",
        security=SEGURANCA_BEARER,
        responses={
            200: AdsFeedViewSchema,
            400: ErrorSchema,
            401: ErrorSchema,
            500: ErrorSchema,
        },
    )
    @protegida
    def ads() -> tuple[dict[str, object], int]:
        page_value = request.args.get("page")
        page = None
        if page_value is not None:
            try:
                page = int(page_value)
            except (TypeError, ValueError):
                return _erro(
                    "Página deve ser um inteiro positivo.",
                    HTTPStatus.BAD_REQUEST,
                )

        repository = app.extensions.get("ad_repository")
        if repository is None:
            return _erro(
                "Erro interno ao buscar anúncios.",
                HTTPStatus.INTERNAL_SERVER_ERROR,
            )

        try:
            result = ListAds(repository).execute(
                usuario=g.usuario,
                page=page,
                search=request.args.get("search"),
                ad_type=request.args.get("type"),
            )
        except ErroDeCasoDeUso as error:
            return _erro(str(error), HTTPStatus.UNAUTHORIZED)
        except ValueError as error:
            return _erro(str(error), HTTPStatus.BAD_REQUEST)
        except Exception:
            current_app.logger.exception("Falha ao consultar o feed.")
            return _erro(
                "Erro interno ao buscar anúncios.",
                HTTPStatus.INTERNAL_SERVER_ERROR,
            )
        return apresenta_feed(result).model_dump(mode="json"), 200

    @app.post(
        "/api/ads",
        security=SEGURANCA_BEARER,
        responses={
            201: AdViewSchema,
            400: ErroPublicacaoSchema,
            401: ErrorSchema,
            403: ErrorSchema,
            413: ErrorSchema,
            415: ErrorSchema,
            503: ErrorSchema,
        },
    )
    @protegida
    def publicar_ad():
        dados, arquivo = _ler_entrada()
        if dados is None:
            if request.mimetype not in {
                "application/json",
                "multipart/form-data",
            }:
                return _erro(
                    "Envie JSON ou multipart/form-data.",
                    HTTPStatus.UNSUPPORTED_MEDIA_TYPE,
                )
            return _erro(
                "O corpo enviado não é um objeto válido.",
                HTTPStatus.BAD_REQUEST,
            )

        arquivos_desconhecidos = set(request.files) - {"imagem"}
        if arquivos_desconhecidos:
            return _erro(
                "Arquivo não permitido.",
                HTTPStatus.UNPROCESSABLE_ENTITY,
                codigo="dados_invalidos",
                campos={
                    campo: "Este arquivo não é permitido."
                    for campo in arquivos_desconhecidos
                },
            )
        anuncio, erros = _validar_anuncio(dados, g.usuario.id)
        if erros:
            return _erro(
                "Dados inválidos.",
                HTTPStatus.UNPROCESSABLE_ENTITY,
                codigo="dados_invalidos",
                campos=erros,
            )

        if app.extensions["anunciante_repository"].buscar_por_usuario_id(
            g.usuario.id
        ) is None:
            return _erro(
                "Complete seu perfil para publicar anúncios.",
                HTTPStatus.FORBIDDEN,
                codigo="perfil_incompleto",
            )

        storage: ImageStorage = app.extensions["image_storage"]
        image_key = None
        try:
            if arquivo is not None:
                image_key = storage.salvar_imagem(
                    arquivo.stream,
                    namespace="anuncios",
                ).chave
            if image_key is not None:
                anuncio = replace(anuncio, image_key=image_key)
            publicado = app.extensions["publicar_anuncio"].executar(anuncio)
        except PerfilIncompleto as error:
            _limpar_imagem(storage, image_key)
            return _erro(
                str(error),
                HTTPStatus.FORBIDDEN,
                codigo="perfil_incompleto",
            )
        except ImagemInvalidaError as error:
            return _erro(
                str(error),
                HTTPStatus.BAD_REQUEST,
                codigo="imagem_invalida",
            )
        except StorageIndisponivelError:
            current_app.logger.exception(
                "Armazenamento de imagem indisponível."
            )
            return _erro(
                "Armazenamento de imagem indisponível.",
                HTTPStatus.SERVICE_UNAVAILABLE,
                codigo="storage_indisponivel",
            )
        except Exception:
            _limpar_imagem(storage, image_key)
            current_app.logger.exception("Falha ao publicar anúncio.")
            return _erro(
                "Erro interno ao publicar anúncio.",
                HTTPStatus.INTERNAL_SERVER_ERROR,
            )

        return apresenta_ad(publicado).model_dump(mode="json"), 201
