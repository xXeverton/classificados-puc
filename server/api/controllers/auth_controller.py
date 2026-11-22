"""HTTP controller for registration, e-mail confirmation, and sessions."""

from dataclasses import dataclass

from flask import g
from flask_openapi3 import APIBlueprint, OpenAPI, Tag
from pydantic import BaseModel

from server.api.autenticacao import SEGURANCA_BEARER, exige_sessao
from server.api.presenters.error_presenter import ErrorSchema
from server.api.presenters.mensagem_presenter import (
    MensagemViewSchema,
    apresenta_mensagem,
)
from server.api.presenters.sessao_presenter import (
    SessaoViewSchema,
    apresenta_sessao,
)
from server.api.presenters.usuario_presenter import (
    UsuarioViewSchema,
    apresenta_usuario,
)
from server.core.usecases.autenticar import Autenticar
from server.core.usecases.cadastrar_usuario import CadastrarUsuario
from server.core.usecases.confirmar_email import ConfirmarEmail
from server.core.usecases.encerrar_sessao import EncerrarSessao
from server.core.usecases.obter_usuario_da_sessao import (
    ObterUsuarioDaSessao,
)
from server.core.usecases.reenviar_confirmacao import ReenviarConfirmacao

MENSAGEM_REENVIO = (
    "Se houver um cadastro pendente para este e-mail, um novo link de "
    "confirmação foi enviado."
)


class CadastroBody(BaseModel):
    nome: str
    email: str
    nome_usuario: str
    vinculo: str
    senha: str
    matricula: str | None = None


class ConfirmacaoBody(BaseModel):
    token: str


class ReenvioBody(BaseModel):
    email: str


class LoginBody(BaseModel):
    identificador: str
    senha: str


@dataclass(frozen=True)
class CasosDeUsoDeAutenticacao:
    cadastrar_usuario: CadastrarUsuario
    confirmar_email: ConfirmarEmail
    reenviar_confirmacao: ReenviarConfirmacao
    autenticar: Autenticar
    encerrar_sessao: EncerrarSessao
    obter_usuario_da_sessao: ObterUsuarioDaSessao


def register_auth_controller(
    app: OpenAPI, casos_de_uso: CasosDeUsoDeAutenticacao
) -> None:
    """Register the /auth routes on the API application."""
    blueprint = APIBlueprint(
        "auth",
        __name__,
        url_prefix="/auth",
        abp_tags=[Tag(name="Autenticação")],
    )
    protegida = exige_sessao(casos_de_uso.obter_usuario_da_sessao)

    @blueprint.post(
        "/cadastro",
        responses={
            201: UsuarioViewSchema, 400: ErrorSchema, 409: ErrorSchema,
        },
    )
    def cadastro(body: CadastroBody):
        usuario = casos_de_uso.cadastrar_usuario.executar(
            nome=body.nome,
            email=body.email,
            nome_usuario=body.nome_usuario,
            matricula=body.matricula,
            vinculo=body.vinculo,
            senha=body.senha,
        )
        return apresenta_usuario(usuario).model_dump(), 201

    @blueprint.post(
        "/confirmacao",
        responses={
            200: UsuarioViewSchema, 400: ErrorSchema, 410: ErrorSchema,
        },
    )
    def confirmacao(body: ConfirmacaoBody):
        usuario = casos_de_uso.confirmar_email.executar(body.token)
        return apresenta_usuario(usuario).model_dump()

    @blueprint.post(
        "/confirmacao/reenviar",
        responses={202: MensagemViewSchema, 400: ErrorSchema},
    )
    def reenviar_confirmacao(body: ReenvioBody):
        casos_de_uso.reenviar_confirmacao.executar(body.email)
        return apresenta_mensagem(MENSAGEM_REENVIO).model_dump(), 202

    @blueprint.post(
        "/login",
        responses={
            200: SessaoViewSchema,
            400: ErrorSchema,
            401: ErrorSchema,
            403: ErrorSchema,
            429: ErrorSchema,
        },
    )
    def login(body: LoginBody):
        resultado = casos_de_uso.autenticar.executar(
            body.identificador, body.senha
        )
        return apresenta_sessao(resultado).model_dump(mode="json")

    @blueprint.post(
        "/logout",
        security=SEGURANCA_BEARER,
        responses={204: None, 401: ErrorSchema},
    )
    @protegida
    def logout():
        casos_de_uso.encerrar_sessao.executar(g.token_sessao)
        return "", 204

    @blueprint.get(
        "/me",
        security=SEGURANCA_BEARER,
        responses={200: UsuarioViewSchema, 401: ErrorSchema},
    )
    @protegida
    def me():
        return apresenta_usuario(g.usuario).model_dump()

    app.register_api(blueprint)
