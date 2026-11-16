"""Rotas HTTP de autenticação e decorator para proteger rotas."""

from dataclasses import dataclass
from functools import wraps
from http import HTTPStatus

from flask import Blueprint, current_app, g, jsonify, request

from domain.erros import (
    CredenciaisInvalidas,
    EmailNaoInstitucional,
    LoginBloqueado,
    TokenInvalido,
)
from use_cases.autenticacao import (
    EntrarComEmail,
    EntrarComLinkMagico,
    ObterUsuarioAutenticado,
    SolicitarLinkMagico,
)
from use_cases.autenticacao.portas import FalhaEnvioEmail, SessaoAutenticada

CHAVE_EXTENSAO = "autenticacao"
_PREFIXO_BEARER = "Bearer "

autenticacao_bp = Blueprint("autenticacao", __name__, url_prefix="/auth")


@dataclass(frozen=True)
class CasosDeUsoAutenticacao:
    entrar_com_email: EntrarComEmail
    solicitar_link_magico: SolicitarLinkMagico
    entrar_com_link_magico: EntrarComLinkMagico
    obter_usuario_autenticado: ObterUsuarioAutenticado


def _casos_de_uso() -> CasosDeUsoAutenticacao:
    return current_app.extensions[CHAVE_EXTENSAO]


def _erro(mensagem: str, status: HTTPStatus):
    return jsonify({"erro": mensagem}), status


def _campo_texto(dados: dict, nome: str) -> str:
    valor = dados.get(nome)
    return valor.strip() if isinstance(valor, str) else ""


def _resposta_sessao(sessao: SessaoAutenticada):
    return jsonify(
        {
            "access_token": sessao.token,
            "token_type": "Bearer",
            "expires_in": sessao.expira_em_segundos,
        }
    )


@autenticacao_bp.post("/login")
def login():
    dados = request.get_json(silent=True) or {}
    email = _campo_texto(dados, "email")
    senha = dados.get("senha") if isinstance(dados.get("senha"), str) else ""
    if not email or not senha:
        return _erro("Informe e-mail e senha.", HTTPStatus.BAD_REQUEST)

    try:
        sessao = _casos_de_uso().entrar_com_email.executar(email, senha)
    except EmailNaoInstitucional as erro:
        return _erro(str(erro), HTTPStatus.BAD_REQUEST)
    except CredenciaisInvalidas as erro:
        return _erro(str(erro), HTTPStatus.UNAUTHORIZED)
    except LoginBloqueado as erro:
        resposta, status = _erro(str(erro), HTTPStatus.TOO_MANY_REQUESTS)
        resposta.headers["Retry-After"] = str(erro.segundos_restantes)
        return resposta, status
    return _resposta_sessao(sessao)


@autenticacao_bp.post("/link-magico")
def solicitar_link_magico():
    email = _campo_texto(request.get_json(silent=True) or {}, "email")
    if not email:
        return _erro("Informe o e-mail.", HTTPStatus.BAD_REQUEST)

    try:
        _casos_de_uso().solicitar_link_magico.executar(email)
    except EmailNaoInstitucional as erro:
        return _erro(str(erro), HTTPStatus.BAD_REQUEST)
    except FalhaEnvioEmail:
        current_app.logger.exception("Falha ao enviar link mágico")
        return _erro(
            "Não foi possível enviar o e-mail agora. Tente mais tarde.",
            HTTPStatus.SERVICE_UNAVAILABLE,
        )
    return (
        jsonify(
            {
                "mensagem": "Se o e-mail estiver cadastrado, você receberá "
                "um link de acesso."
            }
        ),
        HTTPStatus.ACCEPTED,
    )


@autenticacao_bp.post("/link-magico/validar")
def validar_link_magico():
    token = _campo_texto(request.get_json(silent=True) or {}, "token")
    if not token:
        return _erro("Informe o token.", HTTPStatus.BAD_REQUEST)

    try:
        sessao = _casos_de_uso().entrar_com_link_magico.executar(token)
    except TokenInvalido as erro:
        return _erro(str(erro), HTTPStatus.UNAUTHORIZED)
    return _resposta_sessao(sessao)


def requer_autenticacao(rota):
    """Exige `Authorization: Bearer <token>` e guarda o usuário em `g`."""

    @wraps(rota)
    def rota_protegida(*args, **kwargs):
        cabecalho = request.headers.get("Authorization", "")
        if not cabecalho.startswith(_PREFIXO_BEARER):
            return _erro("Autenticação necessária.", HTTPStatus.UNAUTHORIZED)

        token = cabecalho[len(_PREFIXO_BEARER):].strip()
        try:
            g.usuario = _casos_de_uso().obter_usuario_autenticado.executar(
                token
            )
        except TokenInvalido as erro:
            return _erro(str(erro), HTTPStatus.UNAUTHORIZED)
        return rota(*args, **kwargs)

    return rota_protegida


@autenticacao_bp.get("/me")
@requer_autenticacao
def usuario_atual():
    usuario = g.usuario
    return jsonify(
        {
            "id": usuario.id,
            "nome": usuario.nome,
            "email": usuario.email,
            "matricula": usuario.matricula,
            "vinculo": usuario.vinculo.value,
        }
    )
