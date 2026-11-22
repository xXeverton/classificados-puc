"""SQLAlchemy persistence models."""

from datetime import UTC, datetime

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    Text,
    UniqueConstraint,
)
from sqlalchemy.engine import Dialect
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.types import TypeDecorator


class UTCDateTime(TypeDecorator[datetime]):
    """Store aware datetimes as naive UTC and load them back as UTC.

    SQLite has no time zone type, so the conversion keeps the core working
    only with timezone-aware UTC values.
    """

    impl = DateTime
    cache_ok = True

    def process_bind_param(
        self, value: datetime | None, dialect: Dialect
    ) -> datetime | None:
        if value is None:
            return None
        if value.tzinfo is None:
            raise ValueError("Datetime sem fuso horário não é aceito.")
        return value.astimezone(UTC).replace(tzinfo=None)

    def process_result_value(
        self, value: datetime | None, dialect: Dialect
    ) -> datetime | None:
        if value is None:
            return None
        return value.replace(tzinfo=UTC)


class Base(DeclarativeBase):
    """Declarative base shared by persistence models."""


class UsuarioModel(Base):
    """Database representation of a user."""

    __tablename__ = "usuarios"
    __table_args__ = (
        CheckConstraint("length(trim(nome)) > 0", name="ck_usuarios_nome"),
        CheckConstraint("length(trim(email)) > 0", name="ck_usuarios_email"),
        CheckConstraint(
            "length(trim(nome_usuario)) > 0 "
            "AND instr(nome_usuario, '@') = 0",
            name="ck_usuarios_nome_usuario",
        ),
        CheckConstraint(
            "length(trim(matricula)) > 0",
            name="ck_usuarios_matricula",
        ),
        CheckConstraint(
            "vinculo IN ('aluno', 'funcionario')",
            name="ck_usuarios_vinculo",
        ),
        CheckConstraint(
            "length(trim(senha_hash)) > 0",
            name="ck_usuarios_senha_hash",
        ),
        CheckConstraint(
            "tentativas_login_falhas >= 0",
            name="ck_usuarios_tentativas_login_falhas",
        ),
        UniqueConstraint("email", name="uq_usuarios_email"),
        UniqueConstraint("nome_usuario", name="uq_usuarios_nome_usuario"),
        UniqueConstraint("matricula", name="uq_usuarios_matricula"),
        {"sqlite_autoincrement": True},
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    nome: Mapped[str] = mapped_column(Text, nullable=False)
    email: Mapped[str] = mapped_column(Text, nullable=False)
    nome_usuario: Mapped[str] = mapped_column(Text, nullable=False)
    matricula: Mapped[str | None] = mapped_column(Text, nullable=True)
    vinculo: Mapped[str] = mapped_column(Text, nullable=False)
    vinculo: Mapped[str] = mapped_column(Text, nullable=False)
    senha_hash: Mapped[str] = mapped_column(Text, nullable=False)
    confirmado_em: Mapped[datetime | None] = mapped_column(
        UTCDateTime, nullable=True
    )
    tentativas_login_falhas: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default="0"
    )
    bloqueado_ate: Mapped[datetime | None] = mapped_column(
        UTCDateTime, nullable=True
    )


class AnuncianteModel(Base):
    """Advertiser profile: optional extension of a user (at most one)."""

    __tablename__ = "anunciantes"
    __table_args__ = (
        CheckConstraint(
            "length(trim(nome_exibicao)) > 0",
            name="ck_anunciantes_nome_exibicao",
        ),
        CheckConstraint(
            "foto_url IS NULL OR length(trim(foto_url)) > 0",
            name="ck_anunciantes_foto_url",
        ),
        UniqueConstraint("usuario_id", name="uq_anunciantes_usuario_id"),
        {"sqlite_autoincrement": True},
    )

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    usuario_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("usuarios.id", ondelete="CASCADE"),
        nullable=False,
    )
    nome_exibicao: Mapped[str] = mapped_column(Text, nullable=False)
    foto_url: Mapped[str | None] = mapped_column(Text, nullable=True)


class ContatoAnuncianteModel(Base):
    """One contact (WhatsApp, phone, e-mail, site or link) of an advertiser.

    The minimum and maximum number of contacts and repeated contacts are
    enforced by the `Anunciante` entity, not by the database.
    """

    __tablename__ = "contatos_anunciante"
    __table_args__ = (
        CheckConstraint(
            "tipo IN ('whatsapp', 'telefone', 'email', 'site', 'link')",
            name="ck_contatos_anunciante_tipo",
        ),
        CheckConstraint("posicao >= 0", name="ck_contatos_anunciante_posicao"),
        CheckConstraint(
            "length(trim(valor)) > 0", name="ck_contatos_anunciante_valor"
        ),
        # Country code: required for phone, optional for WhatsApp (empty
        # means "by link"), forbidden for the other kinds.
        CheckConstraint(
            "CASE tipo WHEN 'telefone' THEN codigo_pais IS NOT NULL "
            "WHEN 'whatsapp' THEN 1 ELSE codigo_pais IS NULL END",
            name="ck_contatos_anunciante_codigo_pais_do_tipo",
        ),
        CheckConstraint(
            "codigo_pais IS NULL OR ("
            "length(codigo_pais) BETWEEN 1 AND 3 "
            "AND codigo_pais NOT GLOB '*[^0-9]*' "
            "AND valor NOT GLOB '*[^0-9]*' "
            "AND length(codigo_pais) + length(valor) BETWEEN 8 AND 15)",
            name="ck_contatos_anunciante_numero",
        ),
        CheckConstraint(
            "tipo <> 'whatsapp' OR codigo_pais IS NOT NULL OR ("
            "valor NOT GLOB '*[ ]*' AND ("
            "valor LIKE 'https://wa.me/_%' "
            "OR valor LIKE 'https://api.whatsapp.com/_%'))",
            name="ck_contatos_anunciante_whatsapp_link",
        ),
        CheckConstraint(
            "tipo <> 'email' OR instr(valor, '@') > 1",
            name="ck_contatos_anunciante_email",
        ),
        CheckConstraint(
            "tipo NOT IN ('site', 'link') OR ("
            "valor LIKE 'https://_%' AND valor NOT GLOB '*[ ]*')",
            name="ck_contatos_anunciante_endereco",
        ),
        CheckConstraint(
            "rotulo IS NULL OR (tipo = 'link' AND length(trim(rotulo)) > 0)",
            name="ck_contatos_anunciante_rotulo",
        ),
        UniqueConstraint(
            "anunciante_id",
            "posicao",
            name="uq_contatos_anunciante_posicao",
        ),
        {"sqlite_autoincrement": True},
    )

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    anunciante_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("anunciantes.id", ondelete="CASCADE"),
        nullable=False,
    )
    posicao: Mapped[int] = mapped_column(Integer, nullable=False)
    tipo: Mapped[str] = mapped_column(Text, nullable=False)
    codigo_pais: Mapped[str | None] = mapped_column(Text, nullable=True)
    valor: Mapped[str] = mapped_column(Text, nullable=False)
    rotulo: Mapped[str | None] = mapped_column(Text, nullable=True)


class TokenDeConfirmacaoModel(Base):
    """Hash of an e-mail confirmation token."""

    __tablename__ = "tokens_confirmacao"
    __table_args__ = (
        UniqueConstraint("token_hash", name="uq_tokens_confirmacao_hash"),
        {"sqlite_autoincrement": True},
    )

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    usuario_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("usuarios.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    token_hash: Mapped[str] = mapped_column(Text, nullable=False)
    expira_em: Mapped[datetime] = mapped_column(UTCDateTime, nullable=False)
    usado_em: Mapped[datetime | None] = mapped_column(
        UTCDateTime, nullable=True
    )


class SessaoModel(Base):
    """Hash of an authenticated session token."""

    __tablename__ = "sessoes"
    __table_args__ = (
        UniqueConstraint("token_hash", name="uq_sessoes_token_hash"),
        {"sqlite_autoincrement": True},
    )

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    usuario_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("usuarios.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    token_hash: Mapped[str] = mapped_column(Text, nullable=False)
    criada_em: Mapped[datetime] = mapped_column(UTCDateTime, nullable=False)
    expira_em: Mapped[datetime] = mapped_column(UTCDateTime, nullable=False)
    revogada_em: Mapped[datetime | None] = mapped_column(
        UTCDateTime, nullable=True
    )


class AdModel(Base):
    """Database representation of an advertisement."""

    __tablename__ = "ads"
    __table_args__ = (
        CheckConstraint(
            "length(trim(title)) BETWEEN 5 AND 80",
            name="ck_ads_title",
        ),
        CheckConstraint(
            "(usuario_id IS NULL AND ("
            "description IS NULL OR length(description) <= 500)) "
            "OR (usuario_id IS NOT NULL AND description IS NOT NULL "
            "AND length(trim(description)) > 0 "
            "AND length(description) <= 500)",
            name="ck_ads_description",
        ),
        CheckConstraint(
            "type IN ('product', 'service', 'event')",
            name="ck_ads_type",
        ),
        CheckConstraint(
            "length(trim(category)) > 0",
            name="ck_ads_category",
        ),
        CheckConstraint(
            "status IN ('published', 'sold', 'expired')",
            name="ck_ads_status",
        ),
        CheckConstraint(
            "estado_conservacao IS NULL OR "
            "estado_conservacao IN ('novo', 'usado_regular')",
            name="ck_ads_estado_conservacao",
        ),
        CheckConstraint(
            "preco_a_combinar IN (0, 1)",
            name="ck_ads_preco_a_combinar",
        ),
        {"sqlite_autoincrement": True},
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    title: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    type: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(Text, nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    image_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        UTCDateTime,
        nullable=False,
    )
    status: Mapped[str] = mapped_column(Text, nullable=False)
    expires_at: Mapped[datetime | None] = mapped_column(
        UTCDateTime,
        nullable=True,
    )
    usuario_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("usuarios.id", ondelete="CASCADE"),
        nullable=True,
    )
    estado_conservacao: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    preco_a_combinar: Mapped[bool] = mapped_column(
        nullable=False,
        default=False,
        server_default="0",
    )
    image_key: Mapped[str | None] = mapped_column(Text, nullable=True)
