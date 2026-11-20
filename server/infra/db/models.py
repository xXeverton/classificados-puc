"""SQLAlchemy persistence models."""

from datetime import UTC, datetime

from sqlalchemy import (
    CheckConstraint,
    DateTime,
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
