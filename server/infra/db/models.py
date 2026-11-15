"""SQLAlchemy persistence models."""

from sqlalchemy import CheckConstraint, Integer, Text, UniqueConstraint
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
