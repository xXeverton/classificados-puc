"""Application entry point and dependency composition root."""

import logging
import os
from collections.abc import Mapping
from datetime import timedelta
from pathlib import Path

from flask import request
from flask_cors import CORS
from flask_openapi3 import Info, OpenAPI
from werkzeug.exceptions import RequestEntityTooLarge

from server.api.controllers.ads_controller import register_ads_controller
from server.api.autenticacao import ESQUEMA_DE_SEGURANCA
from server.api.controllers.auth_controller import (
    CasosDeUsoDeAutenticacao,
    register_auth_controller,
)
from server.api.controllers.health_controller import (
    register_health_controller,
)
from server.api.controllers.perfil_anunciante_controller import (
    CasosDeUsoDePerfilAnunciante,
    register_perfil_anunciante_controller,
)
from server.api.erros_http import (
    STATUS_DE_VALIDACAO,
    registrar_tratamento_de_erros,
    resposta_de_validacao,
)
from server.core.interfaces.enviador_de_email_interface import (
    EnviadorDeEmailInterface,
)
from server.core.usecases.autenticar import Autenticar
from server.core.usecases.cadastrar_usuario import CadastrarUsuario
from server.core.usecases.confirmar_email import ConfirmarEmail
from server.core.usecases.emissor_de_confirmacao import EmissorDeConfirmacao
from server.core.usecases.encerrar_sessao import EncerrarSessao
from server.core.usecases.obter_usuario_da_sessao import (
    ObterUsuarioDaSessao,
)
from server.core.usecases.obter_perfil_anunciante import (
    ObterPerfilAnunciante,
)
from server.core.usecases.publicar_anuncio import PublicarAnuncio
from server.core.usecases.reenviar_confirmacao import ReenviarConfirmacao
from server.core.usecases.salvar_perfil_anunciante import (
    SalvarPerfilAnunciante,
)
from server.infra.db.database import (
    create_database_engine,
    create_session_factory,
    initialize_database,
)
from server.infra.gateways.anunciante_repository_sqlalchemy import (
    AnuncianteRepositorySQLAlchemy,
)
from server.infra.gateways.sessao_repository_sqlalchemy import (
    SessaoRepositorySQLAlchemy,
)
from server.infra.gateways.token_confirmacao_repository_sqlalchemy import (
    TokenConfirmacaoRepositorySQLAlchemy,
)
from server.infra.gateways.usuario_repository_sqlalchemy import (
    UsuarioRepositorySQLAlchemy,
)
from server.infra.gateways.ad_repository_sqlalchemy import (
    AdRepositorySQLAlchemy,
)
from server.infra.storage.initialization import init_storage
from server.infra.storage.storage import ImageStorage
from server.infra.services import enviador_email_log
from server.infra.services.armazenamento_foto_local import (
    ArmazenamentoDeFotoLocal,
)
from server.infra.services.enviador_email_log import EnviadorDeEmailLog
from server.infra.services.enviador_email_smtp import (
    ConfiguracaoSMTP,
    EnviadorDeEmailSMTP,
)
from server.infra.services.gerador_token_secrets import GeradorDeTokenSecrets
from server.infra.services.hasher_senha_werkzeug import HasherDeSenhaWerkzeug
from server.infra.services.relogio_sistema import RelogioSistema

CONFIRMACAO_URL_BASE_PADRAO = "http://localhost:5173/confirmar-email"
SESSAO_DURACAO_HORAS_PADRAO = 8
# 2 MB photo + the other form fields (plan.md, "Tamanho da requisição").
TAMANHO_MAXIMO_REQUISICAO_BYTES = 3 * 1024 * 1024
FOTOS_PERFIL_DIR_PADRAO = str(
    Path(__file__).resolve().parent / "uploads" / "fotos_perfil"
)
_CONFIGURACAO_SMTP_OBRIGATORIA = (
    "SMTP_HOST",
    "SMTP_PORT",
    "SMTP_USUARIO",
    "SMTP_SENHA",
    "EMAIL_REMETENTE",
)


def create_app(
    config: Mapping[str, object] | None = None,
    *,
    image_storage: ImageStorage | None = None,
) -> OpenAPI:
    """Create the API and wire its infrastructure dependencies.

    Tests may override `RELOGIO`, `ENVIADOR_EMAIL`, and `GERADOR_TOKEN`
    through `config`.
    """
    app = OpenAPI(
        __name__,
        info=Info(
            title="Classificados PUC API",
            version="1.0.0",
            description=(
                "API da plataforma de classificados da comunidade PUC."
            ),
        ),
        security_schemes={
            ESQUEMA_DE_SEGURANCA: {"type": "http", "scheme": "bearer"}
        },
        validation_error_status=STATUS_DE_VALIDACAO,
        validation_error_callback=resposta_de_validacao,
    )
    app.config.from_mapping(
        DATABASE_URL=os.environ.get("DATABASE_URL"),
        CORS_ORIGINS=[
            origin.strip()
            for origin in os.environ.get("CORS_ORIGINS", "").split(",")
            if origin.strip()
        ],
        EMAIL_BACKEND=os.environ.get("EMAIL_BACKEND", "log"),
        SMTP_HOST=os.environ.get("SMTP_HOST"),
        SMTP_PORT=os.environ.get("SMTP_PORT"),
        SMTP_USUARIO=os.environ.get("SMTP_USUARIO"),
        SMTP_SENHA=os.environ.get("SMTP_SENHA"),
        EMAIL_REMETENTE=os.environ.get("EMAIL_REMETENTE"),
        CONFIRMACAO_URL_BASE=os.environ.get(
            "CONFIRMACAO_URL_BASE", CONFIRMACAO_URL_BASE_PADRAO
        ),
        SESSAO_DURACAO_HORAS=os.environ.get(
            "SESSAO_DURACAO_HORAS", SESSAO_DURACAO_HORAS_PADRAO
        ),
        FOTOS_PERFIL_DIR=os.environ.get(
            "FOTOS_PERFIL_DIR", FOTOS_PERFIL_DIR_PADRAO
        ),
        MAX_CONTENT_LENGTH=TAMANHO_MAXIMO_REQUISICAO_BYTES,
    )
    if config is not None:
        app.config.update(config)

    engine = create_database_engine(app.config["DATABASE_URL"])
    initialize_database(engine)
    session_factory = create_session_factory(engine)
    app.extensions["database_engine"] = engine
    app.extensions["session_factory"] = session_factory
    storage = init_storage(app, image_storage)
    app.config["MAX_CONTENT_LENGTH"] = max(
        TAMANHO_MAXIMO_REQUISICAO_BYTES,
        storage.config.max_image_bytes + 1024 * 1024,
    )
    anunciante_repository = AnuncianteRepositorySQLAlchemy(session_factory)
    relogio = app.config.get("RELOGIO") or RelogioSistema()
    ad_repository = AdRepositorySQLAlchemy(session_factory, storage)
    app.extensions["ad_repository"] = ad_repository
    app.extensions["anunciante_repository"] = anunciante_repository
    app.extensions["publicar_anuncio"] = PublicarAnuncio(
        ad_repository,
        anunciante_repository,
        relogio,
    )

    casos_de_uso = _montar_casos_de_uso(app, session_factory, relogio)
    app.extensions["casos_de_uso_autenticacao"] = casos_de_uso
    casos_de_uso_perfil = _montar_casos_de_uso_de_perfil(
        app,
        session_factory,
        casos_de_uso.obter_usuario_da_sessao,
        anunciante_repository,
    )

    cors_origins = app.config["CORS_ORIGINS"]
    if cors_origins:
        CORS(app, origins=cors_origins)

    registrar_tratamento_de_erros(app)
    register_health_controller(app)
    register_auth_controller(app, casos_de_uso)
    register_ads_controller(app, casos_de_uso.obter_usuario_da_sessao)
    register_perfil_anunciante_controller(app, casos_de_uso_perfil)

    @app.before_request
    def limitar_requisicoes_fora_da_publicacao():
        if (
            request.endpoint != "publicar_ad"
            and request.content_length is not None
            and request.content_length > TAMANHO_MAXIMO_REQUISICAO_BYTES
        ):
            raise RequestEntityTooLarge()

    return app


def _montar_casos_de_uso(app: OpenAPI, session_factory, relogio):
    usuarios = UsuarioRepositorySQLAlchemy(session_factory)
    tokens = TokenConfirmacaoRepositorySQLAlchemy(session_factory)
    sessoes = SessaoRepositorySQLAlchemy(session_factory)
    app.extensions["usuario_repository"] = usuarios

    gerador_token = app.config.get("GERADOR_TOKEN") or GeradorDeTokenSecrets()
    enviador_email = app.config.get("ENVIADOR_EMAIL") or _criar_enviador(
        app.config
    )
    hasher_senha = HasherDeSenhaWerkzeug()
    emissor = EmissorDeConfirmacao(
        tokens,
        gerador_token,
        enviador_email,
        relogio,
        str(app.config["CONFIRMACAO_URL_BASE"]),
    )
    obter_usuario = ObterUsuarioDaSessao(sessoes, usuarios, relogio)
    return CasosDeUsoDeAutenticacao(
        cadastrar_usuario=CadastrarUsuario(
            usuarios, tokens, hasher_senha, relogio, emissor
        ),
        confirmar_email=ConfirmarEmail(usuarios, tokens, relogio),
        reenviar_confirmacao=ReenviarConfirmacao(usuarios, emissor),
        autenticar=Autenticar(
            usuarios,
            sessoes,
            hasher_senha,
            gerador_token,
            relogio,
            _duracao_sessao(app.config["SESSAO_DURACAO_HORAS"]),
        ),
        encerrar_sessao=EncerrarSessao(sessoes, relogio),
        obter_usuario_da_sessao=obter_usuario,
    )


def _montar_casos_de_uso_de_perfil(
    app: OpenAPI,
    session_factory,
    obter_usuario_da_sessao,
    anunciantes: AnuncianteRepositorySQLAlchemy,
) -> CasosDeUsoDePerfilAnunciante:
    fotos = ArmazenamentoDeFotoLocal(str(app.config["FOTOS_PERFIL_DIR"]))
    return CasosDeUsoDePerfilAnunciante(
        obter_perfil=ObterPerfilAnunciante(anunciantes),
        salvar_perfil=SalvarPerfilAnunciante(anunciantes, fotos),
        obter_usuario_da_sessao=obter_usuario_da_sessao,
        fotos=fotos,
    )


def _criar_enviador(config: Mapping[str, object]) -> EnviadorDeEmailInterface:
    backend = config["EMAIL_BACKEND"]
    if backend == "log":
        _exibir_log_de_emails()
        return EnviadorDeEmailLog()
    if backend != "smtp":
        raise ValueError(
            f"EMAIL_BACKEND inválido: {backend!r}. Use 'log' ou 'smtp'."
        )
    ausentes = [
        nome for nome in _CONFIGURACAO_SMTP_OBRIGATORIA if not config.get(nome)
    ]
    if ausentes:
        raise ValueError(
            "EMAIL_BACKEND=smtp exige as variáveis: " + ", ".join(ausentes)
        )
    return EnviadorDeEmailSMTP(
        ConfiguracaoSMTP(
            host=str(config["SMTP_HOST"]),
            porta=_inteiro(config["SMTP_PORT"], "SMTP_PORT"),
            usuario=str(config["SMTP_USUARIO"]),
            senha=str(config["SMTP_SENHA"]),
            remetente=str(config["EMAIL_REMETENTE"]),
        )
    )


def _exibir_log_de_emails() -> None:
    """Show logged e-mails in the terminal; Python hides INFO by default."""
    logger = logging.getLogger(enviador_email_log.__name__)
    logger.setLevel(logging.INFO)
    if not logger.handlers:
        logger.addHandler(logging.StreamHandler())


def _duracao_sessao(horas: object) -> timedelta:
    valor = _inteiro(horas, "SESSAO_DURACAO_HORAS")
    if valor <= 0:
        raise ValueError("SESSAO_DURACAO_HORAS deve ser maior que zero.")
    return timedelta(hours=valor)


def _inteiro(valor: object, nome: str) -> int:
    try:
        return int(valor)
    except (TypeError, ValueError):
        raise ValueError(f"{nome} deve ser um número inteiro.") from None


if __name__ == "__main__":
    create_app().run(debug=True)
