"""Ponto de entrada da aplicação Flask (camada Frameworks & Drivers)."""

import secrets
from datetime import timedelta
from pathlib import Path

from flask import Flask, current_app, jsonify, request
from werkzeug.exceptions import HTTPException, InternalServerError

from app.config import carregar_config
from app.database import init_app as init_database
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
from infra.seguranca.servico_token_jwt import ServicoTokenJwt
from infra.seguranca.verificador_senha_werkzeug import (
    VerificadorSenhaWerkzeug,
)
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


def create_app(
    config: dict | None = None,
    *,
    usuarios: UsuarioRepository | None = None,
    enviador_email: EnviadorEmail | None = None,
    relogio: Relogio | None = None,
) -> Flask:
    """Cria e configura a instância da aplicação Flask (app factory).

    As dependências opcionais permitem trocar implementações nos testes.
    """
    app = Flask(__name__)
    app.config.update(carregar_config(config))
    app.config.setdefault(
        "DATABASE",
        str(Path(app.instance_path) / "classificados.sqlite3"),
    )
    init_database(app)

    if not app.config["JWT_SECRET"]:
        # Sem segredo fixo, os tokens deixam de valer a cada reinício.
        app.logger.warning("JWT_SECRET não definido; usando um temporário.")
        app.config["JWT_SECRET"] = secrets.token_urlsafe(32)

    app.extensions[CHAVE_EXTENSAO] = _montar_autenticacao(
        config=app.config,
        usuarios=usuarios or UsuarioRepositoryMemoria(),
        enviador_email=enviador_email or _criar_enviador_email(app.config),
        relogio=relogio or RelogioSistema(),
    )

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


if __name__ == "__main__":
    create_app().run(debug=True)
