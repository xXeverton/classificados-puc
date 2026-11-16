"""JSON API routes for announcements."""

import json
import re
from decimal import Decimal, InvalidOperation
from http import HTTPStatus
from typing import Any, NoReturn

from flask import Blueprint, abort, current_app, g, jsonify, request

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
from use_cases.verificar_perfil_completo import (
    CHAVE_EXTENSAO_PERFIL_COMPLETO,
)

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
_MENSAGEM_PRECO_INVALIDO = (
    "Informe um preço válido (de 0 a 9999999999,99, com até duas "
    "casas decimais)."
)


def _rejeitar_constante_json(valor: str) -> NoReturn:
    raise ValueError(f"Constante JSON não permitida: {valor}")


def _preco_decimal(valor: Any) -> Decimal | None:
    if isinstance(valor, bool):
        return None
    if isinstance(valor, Decimal):
        preco = valor
    elif isinstance(valor, int):
        preco = Decimal(valor)
    elif (
        isinstance(valor, str)
        and _PADRAO_PRECO.fullmatch(valor) is not None
    ):
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
    for campo in sorted(set(dados) - _CAMPOS_PERMITIDOS):
        erros[campo] = "Este campo não é permitido."

    titulo_bruto = dados.get("titulo")
    titulo = titulo_bruto.strip(" ") if isinstance(titulo_bruto, str) else ""
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
    estado = None
    if categoria == "produto":
        if estado_bruto is None:
            erros["estado_conservacao"] = (
                "Informe o estado de conservação do produto."
            )
        elif (
            not isinstance(estado_bruto, str)
            or estado_bruto not in ESTADOS_CONSERVACAO
        ):
            erros["estado_conservacao"] = "Estado de conservação inválido."
        else:
            estado = estado_bruto
    elif categoria in {"servico", "evento"} and estado_bruto is not None:
        erros["estado_conservacao"] = (
            "Estado de conservação não se aplica a serviço ou evento."
        )

    descricao_bruta = dados.get("descricao")
    descricao = descricao_bruta if isinstance(descricao_bruta, str) else ""
    if (
        not descricao.strip(" ")
        or len(descricao) > DESCRICAO_MAX_CARACTERES
    ):
        erros["descricao"] = (
            "Informe uma descrição não vazia de até 500 caracteres."
        )

    preco_a_combinar = dados.get("preco_a_combinar", False)
    preco = None
    if not isinstance(preco_a_combinar, bool):
        erros["preco_a_combinar"] = (
            "Informe se o preço é a combinar."
        )
    elif preco_a_combinar:
        if dados.get("preco") is not None:
            erros["preco"] = (
                "Não envie um preço quando selecionar 'A combinar'."
            )
    else:
        if "preco" not in dados:
            erros["preco"] = _MENSAGEM_PRECO_INVALIDO
        else:
            preco = _preco_decimal(dados["preco"])
            if preco is None:
                erros["preco"] = _MENSAGEM_PRECO_INVALIDO

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
    database = get_db()
    usuario_existe = database.execute(
        "SELECT 1 FROM usuarios WHERE id = ?",
        (g.usuario.id,),
    ).fetchone()
    if usuario_existe is None:
        return (
            jsonify({"erro": "Autenticação necessária."}),
            HTTPStatus.UNAUTHORIZED,
        )

    verificador_perfil = current_app.extensions[
        CHAVE_EXTENSAO_PERFIL_COMPLETO
    ]
    if not verificador_perfil.esta_completo(g.usuario.id):
        return (
            jsonify(
                {
                    "codigo": "perfil_incompleto",
                    "erro": "Complete seu perfil para publicar anúncios.",
                }
            ),
            HTTPStatus.FORBIDDEN,
        )

    dados = _ler_corpo_json()
    anuncio, erros = _validar_dados(dados, g.usuario.id)
    if erros:
        return (
            jsonify({"erro": "Dados inválidos.", "campos": erros}),
            HTTPStatus.UNPROCESSABLE_ENTITY,
        )

    publicado = PublicarAnuncio(
        RepositorioAnuncioSQLite(database)
    ).executar(anuncio)
    return jsonify(_anuncio_json(publicado)), HTTPStatus.CREATED
