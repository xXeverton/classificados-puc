"""JSON API routes for announcements."""

import json
import re
from decimal import Decimal, InvalidOperation
from http import HTTPStatus
from typing import Any, NoReturn

from flask import Blueprint, abort, g, jsonify, request

from app.database import get_db
from app.routes.autenticacao import requer_autenticacao
from domain.anuncio import (
    CATEGORIAS,
    DESCRICAO_MAX_CARACTERES,
    ESTADOS_CONSERVACAO,
    PRECO_MAXIMO,
    TITULO_MAX_CARACTERES,
    TITULO_MIN_CARACTERES,
    Anuncio,
    AnuncioPublicado,
)
from infra.repositories.anuncio_sqlite import RepositorioAnuncioSQLite
from use_cases.publicar_anuncio import PublicarAnuncio

api_anuncios_bp = Blueprint("api_anuncios", __name__, url_prefix="/api")
MAX_CORPO_BYTES = 64 * 1024
_PADRAO_PRECO = re.compile(r"[0-9]+(?:[,.][0-9]{1,2})?")
_CAMPOS_PERMITIDOS = {
    "titulo",
    "categoria",
    "estado_conservacao",
    "descricao",
    "preco_a_combinar",
    "preco",
}


def _rejeitar_constante_json(valor: str) -> NoReturn:
    raise ValueError(f"Constante JSON não permitida: {valor}")


def _ler_corpo_json() -> dict[str, Any]:
    if not request.is_json:
        abort(
            HTTPStatus.UNSUPPORTED_MEDIA_TYPE,
            description="Envie o corpo como JSON.",
        )
    if (
        request.content_length is not None
        and request.content_length > MAX_CORPO_BYTES
    ):
        abort(
            HTTPStatus.REQUEST_ENTITY_TOO_LARGE,
            description="O corpo da requisição excede 64 KiB.",
        )

    corpo = request.stream.read(MAX_CORPO_BYTES + 1)
    if len(corpo) > MAX_CORPO_BYTES:
        abort(
            HTTPStatus.REQUEST_ENTITY_TOO_LARGE,
            description="O corpo da requisição excede 64 KiB.",
        )

    try:
        dados = json.loads(
            corpo,
            parse_float=Decimal,
            parse_constant=_rejeitar_constante_json,
        )
    except (UnicodeDecodeError, ValueError):
        abort(
            HTTPStatus.BAD_REQUEST,
            description="O corpo JSON é inválido.",
        )
    if not isinstance(dados, dict):
        abort(
            HTTPStatus.BAD_REQUEST,
            description="O corpo JSON deve ser um objeto.",
        )
    return dados


def _validar_dados(
    dados: dict[str, Any], id_anunciante: int
) -> tuple[Anuncio | None, dict[str, str]]:
    erros: dict[str, str] = {}
    if set(dados) - _CAMPOS_PERMITIDOS:
        erros["geral"] = "A requisição contém campos não permitidos."

    titulo_bruto = dados.get("titulo")
    titulo = titulo_bruto.strip() if isinstance(titulo_bruto, str) else ""
    if not TITULO_MIN_CARACTERES <= len(titulo) <= TITULO_MAX_CARACTERES:
        erros["titulo"] = "O título deve ter entre 5 e 80 caracteres."

    categoria_bruta = dados.get("categoria")
    categoria = (
        categoria_bruta
        if isinstance(categoria_bruta, str)
        and categoria_bruta in CATEGORIAS
        else ""
    )
    if not categoria:
        erros["categoria"] = (
            "Escolha uma categoria: produto, serviço ou evento."
        )

    estado_bruto = dados.get("estado_conservacao")
    estado = (
        estado_bruto
        if isinstance(estado_bruto, str)
        and estado_bruto in ESTADOS_CONSERVACAO
        else None
    )
    if categoria == "produto":
        if estado is None:
            erros["estado_conservacao"] = (
                "Informe o estado de conservação do produto."
            )
    elif categoria and "estado_conservacao" in dados:
        erros["estado_conservacao"] = (
            "Estado de conservação só pode ser enviado para produto."
        )
    else:
        estado = None

    descricao_bruta = dados.get("descricao")
    descricao = (
        descricao_bruta.strip()
        if isinstance(descricao_bruta, str)
        else ""
    )
    if not descricao or len(descricao) > DESCRICAO_MAX_CARACTERES:
        erros["descricao"] = (
            "Informe uma descrição não vazia de até 500 caracteres."
        )

    preco_a_combinar = dados.get("preco_a_combinar")
    preco = None
    if not isinstance(preco_a_combinar, bool):
        erros["preco_a_combinar"] = (
            "Informe se o preço é a combinar."
        )
    elif preco_a_combinar:
        if "preco" in dados:
            erros["preco"] = (
                "Não envie um preço quando selecionar 'A combinar'."
            )
    else:
        preco_bruto = dados.get("preco")
        if (
            not isinstance(preco_bruto, str)
            or _PADRAO_PRECO.fullmatch(preco_bruto) is None
        ):
            erros["preco"] = (
                "Informe um valor válido, de 0 a 9.999.999.999,99, "
                "com até duas casas decimais."
            )
        else:
            try:
                preco = Decimal(preco_bruto.replace(",", "."))
            except InvalidOperation:
                erros["preco"] = (
                    "Informe um valor válido, de 0 a 9.999.999.999,99, "
                    "com até duas casas decimais."
                )
            if preco is not None and (
                not preco.is_finite()
                or preco < 0
                or preco > PRECO_MAXIMO
            ):
                erros["preco"] = (
                    "Informe um valor válido, de 0 a 9.999.999.999,99, "
                    "com até duas casas decimais."
                )

    if erros:
        return None, erros

    return (
        Anuncio(
            id_anunciante=id_anunciante,
            titulo=titulo,
            categoria=categoria,
            estado_conservacao=estado,
            descricao=descricao,
            preco=preco,
        ),
        {},
    )


def _anuncio_json(anuncio: AnuncioPublicado) -> dict[str, Any]:
    return {
        "id": anuncio.id,
        "id_anunciante": anuncio.id_anunciante,
        "nome_anunciante": anuncio.nome_anunciante,
        "titulo": anuncio.titulo,
        "categoria": anuncio.categoria,
        "estado_conservacao": anuncio.estado_conservacao,
        "descricao": anuncio.descricao,
        "preco": (
            format(anuncio.preco, ".2f")
            if anuncio.preco is not None
            else None
        ),
        "preco_a_combinar": anuncio.preco is None,
        "created_at": anuncio.created_at,
    }


@api_anuncios_bp.route("/ads", methods=["POST"])
@requer_autenticacao
def criar_anuncio():
    dados = _ler_corpo_json()
    anuncio, erros = _validar_dados(dados, g.usuario.id)
    if erros:
        return (
            jsonify({"erro": "Dados inválidos.", "campos": erros}),
            HTTPStatus.UNPROCESSABLE_ENTITY,
        )

    publicado = PublicarAnuncio(
        RepositorioAnuncioSQLite(get_db())
    ).executar(anuncio)
    return jsonify(_anuncio_json(publicado)), HTTPStatus.CREATED
