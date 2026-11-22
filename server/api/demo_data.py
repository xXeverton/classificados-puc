"""Seed the local database with an account and ads for manual UI testing."""

from datetime import datetime, timedelta

from sqlalchemy import or_, select
from sqlalchemy.orm import sessionmaker
from werkzeug.security import generate_password_hash

from server.core.entities.anunciante import Anunciante
from server.core.entities.contato import Contato
from server.infra.db.models import AdModel, UsuarioModel
from server.infra.gateways.anunciante_repository_sqlalchemy import (
    AnuncianteRepositorySQLAlchemy,
)

DEMO_EMAIL = "usuario.teste@aluno.puc-rio.br"
DEMO_USERNAME = "demo-classificados"
DEMO_AD_TITLES = (
    "Demo: Caderno universitário",
    "Demo: Aulas de cálculo",
    "Demo: Feira de livros",
    "Demo: Mochila universitária",
    "Demo: Aulas de inglês",
    "Demo: Monitor para estudos",
    "Demo: Apostilas de biologia",
    "Demo: Revisão para provas",
)


def create_demo_data(
    session_factory: sessionmaker,
    password: str,
    now: datetime,
) -> int:
    """Create the reserved demo user, advertiser profile and sample ads.

    Repeated calls update the demo password and add only missing sample data.
    Existing accounts that collide with either reserved identifier are kept
    untouched and rejected.
    """
    password_hash = generate_password_hash(password)
    with session_factory.begin() as session:
        users = session.scalars(
            select(UsuarioModel).where(
                or_(
                    UsuarioModel.email == DEMO_EMAIL,
                    UsuarioModel.nome_usuario == DEMO_USERNAME,
                )
            )
        ).all()
        if len(users) > 1 or (
            users
            and (
                users[0].email != DEMO_EMAIL
                or users[0].nome_usuario != DEMO_USERNAME
            )
        ):
            raise ValueError(
                "Os identificadores reservados da conta demo já estão em uso."
            )

        if users:
            user = users[0]
            user.senha_hash = password_hash
            user.confirmado_em = user.confirmado_em or now
            user.tentativas_login_falhas = 0
            user.bloqueado_ate = None
        else:
            user = UsuarioModel(
                nome="Usuário de teste",
                email=DEMO_EMAIL,
                nome_usuario=DEMO_USERNAME,
                matricula=None,
                vinculo="aluno",
                senha_hash=password_hash,
                confirmado_em=now,
            )
            session.add(user)
            session.flush()

        user_id = user.id
        existing_titles = set(
            session.scalars(
                select(AdModel.title).where(
                    AdModel.usuario_id == user_id,
                    AdModel.title.in_(DEMO_AD_TITLES),
                )
            )
        )
        samples = _sample_ads(user_id, now)
        missing_ads = [
            ad for ad in samples if ad.title not in existing_titles
        ]
        session.add_all(missing_ads)

    advertisers = AnuncianteRepositorySQLAlchemy(session_factory)
    if advertisers.buscar_por_usuario_id(user_id) is None:
        advertisers.salvar(
            Anunciante(
                usuario_id=user_id,
                nome_exibicao="Usuário de teste",
                contatos=(
                    Contato.criar("email", "contato@exemplo.com"),
                ),
            )
        )

    return len(missing_ads)


def _sample_ads(user_id: int, now: datetime) -> list[AdModel]:
    return [
        AdModel(
            title=DEMO_AD_TITLES[0],
            description="Caderno em ótimo estado para testar o feed.",
            type="product",
            category="Livros",
            price=25.0,
            created_at=now - timedelta(days=1),
            status="published",
            expires_at=now + timedelta(days=29),
            usuario_id=user_id,
            estado_conservacao="usado_regular",
        ),
        AdModel(
            title=DEMO_AD_TITLES[1],
            description="Aulas de cálculo para testar serviços.",
            type="service",
            category="Educação",
            price=50.0,
            created_at=now - timedelta(days=31),
            status="expired",
            expires_at=now - timedelta(days=1),
            usuario_id=user_id,
        ),
        AdModel(
            title=DEMO_AD_TITLES[2],
            description="Evento de demonstração para testar estados.",
            type="event",
            category="Eventos",
            price=0.0,
            created_at=now - timedelta(days=2),
            status="sold",
            expires_at=now + timedelta(days=28),
            usuario_id=user_id,
            preco_a_combinar=True,
        ),
        AdModel(
            title=DEMO_AD_TITLES[3],
            description="Mochila usada em bom estado para o dia a dia.",
            type="product",
            category="Acessórios",
            price=65.0,
            created_at=now - timedelta(days=3),
            status="published",
            expires_at=now + timedelta(days=27),
            usuario_id=user_id,
            estado_conservacao="usado_regular",
        ),
        AdModel(
            title=DEMO_AD_TITLES[4],
            description="Aulas de inglês para praticar conversação.",
            type="service",
            category="Educação",
            price=70.0,
            created_at=now - timedelta(days=5),
            status="published",
            expires_at=now + timedelta(days=25),
            usuario_id=user_id,
        ),
        AdModel(
            title=DEMO_AD_TITLES[5],
            description="Monitor para estudos em ótimo estado.",
            type="product",
            category="Eletrônicos",
            price=350.0,
            created_at=now - timedelta(days=7),
            status="published",
            expires_at=now + timedelta(days=23),
            usuario_id=user_id,
            estado_conservacao="usado_regular",
        ),
        AdModel(
            title=DEMO_AD_TITLES[6],
            description="Apostilas de biologia para estudantes.",
            type="product",
            category="Livros",
            price=30.0,
            created_at=now - timedelta(days=45),
            status="expired",
            expires_at=now - timedelta(days=15),
            usuario_id=user_id,
            estado_conservacao="usado_regular",
        ),
        AdModel(
            title=DEMO_AD_TITLES[7],
            description="Revisão de conteúdo para provas da graduação.",
            type="service",
            category="Educação",
            price=60.0,
            created_at=now - timedelta(days=60),
            status="expired",
            expires_at=now - timedelta(days=30),
            usuario_id=user_id,
        ),
    ]
