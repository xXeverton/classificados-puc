"""HTTP controller for the advertiser profile and its photos."""

import json
from dataclasses import dataclass

from flask import Response, g, request
from flask_openapi3 import APIBlueprint, OpenAPI, Tag
from pydantic import BaseModel
from werkzeug.datastructures import FileStorage

from server.api.autenticacao import SEGURANCA_BEARER, exige_sessao
from server.api.presenters.anunciante_presenter import (
    AnuncianteViewSchema,
    apresenta_anunciante,
)
from server.api.presenters.error_presenter import ErrorSchema
from server.core.interfaces.armazenamento_de_foto_interface import (
    ArmazenamentoDeFotoInterface,
)
from server.core.usecases.erros import DadosInvalidos
from server.core.usecases.obter_perfil_anunciante import (
    ObterPerfilAnunciante,
)
from server.core.usecases.obter_usuario_da_sessao import (
    ObterUsuarioDaSessao,
)
from server.core.usecases.salvar_perfil_anunciante import (
    DadosDeContato,
    SalvarPerfilAnunciante,
)

PREFIXO_FOTOS = "/fotos-perfil/"
_TIPO_POR_EXTENSAO = {
    "jpg": "image/jpeg",
    "png": "image/png",
    "webp": "image/webp",
}
_VALORES_VERDADEIROS = ("true", "1", "on", "yes")
_MENSAGEM_CONTATOS = (
    "Os contatos devem ser enviados como uma lista em JSON de objetos."
)
_CAMPOS_DE_CONTATO = ("tipo", "valor", "codigo_pais", "rotulo")


class ArquivoDaFotoPath(BaseModel):
    arquivo: str


@dataclass(frozen=True)
class CasosDeUsoDePerfilAnunciante:
    obter_perfil: ObterPerfilAnunciante
    salvar_perfil: SalvarPerfilAnunciante
    obter_usuario_da_sessao: ObterUsuarioDaSessao
    fotos: ArmazenamentoDeFotoInterface


def _contatos_do_formulario(texto: str) -> list[DadosDeContato]:
    """Parse the JSON list sent in the `contatos` field."""
    try:
        itens = json.loads(texto)
    except ValueError:
        raise DadosInvalidos(_MENSAGEM_CONTATOS) from None
    if not isinstance(itens, list) or not all(
        isinstance(item, dict) for item in itens
    ):
        raise DadosInvalidos(_MENSAGEM_CONTATOS)

    contatos = []
    for item in itens:
        textos = {campo: item.get(campo) for campo in _CAMPOS_DE_CONTATO}
        if not all(
            valor is None or isinstance(valor, str)
            for valor in textos.values()
        ):
            raise DadosInvalidos(_MENSAGEM_CONTATOS)
        contatos.append(
            DadosDeContato(
                tipo=textos["tipo"] or "",
                valor=textos["valor"] or "",
                codigo_pais=textos["codigo_pais"],
                rotulo=textos["rotulo"],
            )
        )
    return contatos


def _foto_enviada() -> bytes | None:
    """Bytes of the `foto` part; a part without file name means no photo."""
    arquivo: FileStorage | None = request.files.get("foto")
    if arquivo is None or not arquivo.filename:
        return None
    return arquivo.read()


def register_perfil_anunciante_controller(
    app: OpenAPI, casos_de_uso: CasosDeUsoDePerfilAnunciante
) -> None:
    """Register the advertiser profile and photo routes."""
    blueprint = APIBlueprint(
        "perfil_anunciante",
        __name__,
        abp_tags=[Tag(name="Perfil de anunciante")],
    )
    protegida = exige_sessao(casos_de_uso.obter_usuario_da_sessao)

    @blueprint.get(
        "/perfil-anunciante",
        security=SEGURANCA_BEARER,
        responses={200: AnuncianteViewSchema, 401: ErrorSchema,
                   404: ErrorSchema},
    )
    @protegida
    def obter_perfil():
        anunciante = casos_de_uso.obter_perfil.executar(g.usuario.id)
        return apresenta_anunciante(anunciante).model_dump()

    # The body is multipart/form-data: nome_exibicao, contatos (JSON list),
    # foto (file) and remover_foto. It is read from `request` because the
    # photo part is optional and browsers may send it empty.
    @blueprint.put(
        "/perfil-anunciante",
        security=SEGURANCA_BEARER,
        responses={
            200: AnuncianteViewSchema,
            400: ErrorSchema,
            401: ErrorSchema,
            413: ErrorSchema,
        },
    )
    @protegida
    def salvar_perfil():
        nome = request.form.get("nome_exibicao")
        contatos = request.form.get("contatos")
        if nome is None or contatos is None:
            faltando = [
                campo
                for campo, valor in (
                    ("nome_exibicao", nome),
                    ("contatos", contatos),
                )
                if valor is None
            ]
            raise DadosInvalidos(
                "Campos ausentes: " + ", ".join(faltando) + "."
            )
        remover = request.form.get("remover_foto", "").strip().lower()
        anunciante = casos_de_uso.salvar_perfil.executar(
            usuario_id=g.usuario.id,
            nome_exibicao=nome,
            contatos=_contatos_do_formulario(contatos),
            foto=_foto_enviada(),
            remover_foto=remover in _VALORES_VERDADEIROS,
        )
        return apresenta_anunciante(anunciante).model_dump()

    @blueprint.get(
        "/fotos-perfil/<arquivo>",
        security=SEGURANCA_BEARER,
        responses={200: None, 401: ErrorSchema, 404: ErrorSchema},
    )
    @protegida
    def foto_de_perfil(path: ArquivoDaFotoPath):
        conteudo = casos_de_uso.fotos.ler(PREFIXO_FOTOS + path.arquivo)
        if conteudo is None:
            return {"message": "Foto não encontrada."}, 404
        extensao = path.arquivo.rsplit(".", 1)[-1]
        return Response(
            conteudo,
            mimetype=_TIPO_POR_EXTENSAO[extensao],
            headers={"X-Content-Type-Options": "nosniff"},
        )

    app.register_api(blueprint)
