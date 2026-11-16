"""Ponto de entrada da aplicação Flask (camada Frameworks & Drivers)."""

import secrets
from datetime import timedelta
from pathlib import Path

from flask import Flask, current_app, jsonify, request
from werkzeug.exceptions import HTTPException, InternalServerError

from app.config import carregar_config
from app.database import init_app as init_database
from app.storage import init_storage
from app.routes.autenticacao import (
    CHAVE_EXTENSAO,
    CasosDeUsoAutenticacao,
    autenticacao_bp,
)
from app.routes.api_anuncios import api_anuncios_bp
from infra.email.enviador_email_console import EnviadorEmailConsole
from infra.email.enviador_email_smtp import EnviadorEmailSmtp
from infra.relogio_sistema import RelogioSistema
from infra.repositories.memoria import (
    LinkMagicoRepositoryMemoria,
    TentativasLoginRepositoryMemoria,
    UsuarioRepositoryMemoria,
)
from infra.repositories.perfil_anunciante_mock import (
    VerificadorPerfilCompletoMock,
)
from infra.seguranca.servico_token_jwt import ServicoTokenJwt
from infra.seguranca.verificador_senha_werkzeug import (
    VerificadorSenhaWerkzeug,
)
from infra.repositories.autenticador_mock import AutenticadorMock
from use_cases.autenticacao import (
    EntrarComEmail,
    EntrarComLinkMagico,
    ObterUsuarioAutenticado,
    SolicitarLinkMagico,
)
from use_cases.autenticacao.portas import (
    EnviadorEmail,
    Relogio,
    UsuarioRepository,
)
from use_cases.verificar_perfil_completo import (
    CHAVE_EXTENSAO_PERFIL_COMPLETO,
    VerificadorPerfilCompleto,
)
from app.routes.anuncios import registrar_rota_novo_anuncio
from infra.storage.storage import ImageStorage
from use_cases.identidade_autenticada import (
    CHAVE_EXTENSAO_AUTENTICADOR,
    Autenticador,
)


def create_app(
    image_storage: ImageStorage | None = None,
    config: dict | None = None,
    *,
    usuarios: UsuarioRepository | None = None,
    enviador_email: EnviadorEmail | None = None,
    relogio: Relogio | None = None,
    verificador_perfil: VerificadorPerfilCompleto | None = None,
    autenticador: Autenticador | None = None,
) -> Flask:
    """Cria a aplicação e permite injetar dependências nos testes."""
    app = Flask(__name__)
    app.config.update(carregar_config(config))
    app.config.setdefault(
        "DATABASE",
        str(Path(app.instance_path) / "classificados.sqlite3"),
    )
    init_database(app)
    init_storage(app, image_storage)

    if not app.config["JWT_SECRET"]:
        app.logger.warning("JWT_SECRET não definido; usando um temporário.")
        app.config["JWT_SECRET"] = secrets.token_urlsafe(32)

    app.extensions[CHAVE_EXTENSAO] = _montar_autenticacao(
        config=app.config,
        usuarios=usuarios or UsuarioRepositoryMemoria(),
        enviador_email=enviador_email or _criar_enviador_email(app.config),
        relogio=relogio or RelogioSistema(),
    )
    app.extensions[CHAVE_EXTENSAO_PERFIL_COMPLETO] = (
        verificador_perfil
        if verificador_perfil is not None
        else VerificadorPerfilCompletoMock()
    )
    autenticador_ativo = (
        AutenticadorMock() if autenticador is None else autenticador
    )
    app.extensions[CHAVE_EXTENSAO_AUTENTICADOR] = autenticador_ativo

    registrar_rota_novo_anuncio(app, autenticador_ativo)
    @app.get("/health")
    def health():
        return {"status": "ok"}

    @app.errorhandler(HTTPException)
    def erro_http(error):
        if not _is_api_request():
            return error
        response = error.get_response()
        response.set_data(
            current_app.json.dumps({"erro": error.description})
        )
        response.content_type = "application/json"
        return response

    @app.errorhandler(InternalServerError)
    def erro_interno_api(error):
        if not _is_api_request():
            return error
        current_app.logger.error("Erro interno ao processar a API.")
        return jsonify({"erro": "Erro interno do servidor."}), 500

    app.register_blueprint(autenticacao_bp)
    app.register_blueprint(api_anuncios_bp)

    return app


def _criar_enviador_email(config: dict) -> EnviadorEmail:
    if not config["SMTP_HOST"]:
        return EnviadorEmailConsole()
    return EnviadorEmailSmtp(
        host=config["SMTP_HOST"],
        porta=config["SMTP_PORT"],
        remetente=config["SMTP_REMETENTE"],
        usuario=config["SMTP_USUARIO"] or None,
        senha=config["SMTP_SENHA"] or None,
        usar_starttls=config["SMTP_STARTTLS"],
    )


def _montar_autenticacao(
    config: dict,
    usuarios: UsuarioRepository,
    enviador_email: EnviadorEmail,
    relogio: Relogio,
) -> CasosDeUsoAutenticacao:
    servico_token = ServicoTokenJwt(
        segredo=config["JWT_SECRET"],
        validade=timedelta(minutes=config["JWT_EXPIRA_MINUTOS"]),
        relogio=relogio,
    )
    links = LinkMagicoRepositoryMemoria()
    return CasosDeUsoAutenticacao(
        entrar_com_email=EntrarComEmail(
            usuarios=usuarios,
            tentativas=TentativasLoginRepositoryMemoria(),
            verificador_senha=VerificadorSenhaWerkzeug(),
            servico_token=servico_token,
            relogio=relogio,
        ),
        solicitar_link_magico=SolicitarLinkMagico(
            usuarios=usuarios,
            links=links,
            enviador_email=enviador_email,
            relogio=relogio,
            url_base=config["URL_LINK_MAGICO"],
        ),
        entrar_com_link_magico=EntrarComLinkMagico(
            links=links,
            usuarios=usuarios,
            servico_token=servico_token,
            relogio=relogio,
        ),
        obter_usuario_autenticado=ObterUsuarioAutenticado(
            servico_token=servico_token, usuarios=usuarios
        ),
    )


def _is_api_request() -> bool:
    return request.path == "/api" or request.path.startswith("/api/")


if __name__ == "__main__":
    create_app().run(debug=True)
