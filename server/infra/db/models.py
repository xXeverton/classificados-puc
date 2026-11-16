"""SQLAlchemy persistence models."""

from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Float,
    Integer,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Declarative base shared by persistence models."""


class UsuarioModel(Base):
    """Database representation of a user."""

    __tablename__ = "usuarios"
    __table_args__ = (
        CheckConstraint("length(trim(nome)) > 0", name="ck_usuarios_nome"),
        CheckConstraint("length(trim(email)) > 0", name="ck_usuarios_email"),
        CheckConstraint(
            "length(trim(matricula)) > 0",
            name="ck_usuarios_matricula",
        ),
        CheckConstraint(
            "length(trim(vinculo)) > 0",
            name="ck_usuarios_vinculo",
        ),
        UniqueConstraint("email", name="uq_usuarios_email"),
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
    matricula: Mapped[str] = mapped_column(Text, nullable=False)
    vinculo: Mapped[str] = mapped_column(Text, nullable=False)


class AdModel(Base):
    """Database representation of an advertisement."""

    __tablename__ = "ads"
    __table_args__ = (
        CheckConstraint("length(trim(title)) > 0", name="ck_ads_title"),
        CheckConstraint(
            "type IN ('product', 'service')",
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
        DateTime(timezone=True),
        nullable=False,
    )
    status: Mapped[str] = mapped_column(Text, nullable=False)
    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
