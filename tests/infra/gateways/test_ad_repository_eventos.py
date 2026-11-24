"""Event fields and featured events in the SQLAlchemy ad repository."""

from datetime import UTC, date, datetime, time, timedelta
from decimal import Decimal

from server.core.entities.anuncio import Anuncio
from server.infra.db.models import AdModel
from tests.infra.gateways.test_ad_repository_gerenciar import preparar

HOJE = date(2026, 11, 20)
CRIADO_EM = datetime(2026, 11, 20, 12, 0, tzinfo=UTC)
# Far enough that the "not expired" rule of the gateway never interferes.
EXPIRA_EM = datetime(2099, 1, 1, tzinfo=UTC)


def evento(data_evento, **extras):
    dados = {
        "usuario_id": 1,
        "titulo": "Feira de profissões",
        "descricao": "Venha conhecer os cursos.",
        "categoria": "evento",
        "preco": None,
        "data_evento": data_evento,
    }
    dados.update(extras)
    return Anuncio(**dados)


def publicar_evento(repositorio, data_evento, criado_em=CRIADO_EM, **extras):
    return repositorio.publish(
        evento(data_evento, **extras), "Ana", criado_em, EXPIRA_EM
    )


def produto():
    return Anuncio(
        usuario_id=1,
        titulo="Livro de Cálculo",
        descricao="Livro em bom estado.",
        categoria="produto",
        preco=Decimal("40"),
        estado_conservacao="novo",
    )


def test_publicar_evento_grava_e_devolve_data_horario_e_local(
    database_engine,
):
    repositorio, session_factory = preparar(database_engine)

    publicado = publicar_evento(
        repositorio,
        HOJE + timedelta(days=3),
        horario_evento=time(14, 30),
        local_evento="Auditório",
    )

    lido = repositorio.buscar_por_id(publicado.id)
    assert lido.type == "event"
    assert lido.data_evento == HOJE + timedelta(days=3)
    assert lido.horario_evento == time(14, 30)
    assert lido.local_evento == "Auditório"
    with session_factory() as session:
        assert session.get(AdModel, publicado.id).data_evento == (
            HOJE + timedelta(days=3)
        )


def test_publicar_produto_nao_tem_campos_de_evento(database_engine):
    repositorio, _ = preparar(database_engine)

    publicado = repositorio.publish(
        produto(), "Ana", CRIADO_EM, EXPIRA_EM
    )

    assert publicado.data_evento is None
    assert publicado.horario_evento is None
    assert publicado.local_evento is None


def test_atualizar_troca_data_horario_e_local_do_evento(database_engine):
    repositorio, _ = preparar(database_engine)
    publicado = publicar_evento(
        repositorio, HOJE + timedelta(days=3), local_evento="Auditório"
    )
    novo_prazo = datetime(2099, 2, 1, tzinfo=UTC)

    editado = repositorio.atualizar(
        publicado.id,
        evento(
            HOJE + timedelta(days=9),
            horario_evento=time(9, 0),
            local_evento=None,
        ),
        expires_at=novo_prazo,
    )

    assert editado.data_evento == HOJE + timedelta(days=9)
    assert editado.horario_evento == time(9, 0)
    assert editado.local_evento is None
    assert editado.expires_at.replace(tzinfo=UTC) == novo_prazo


def test_destaques_ordenam_por_data_depois_por_publicacao(database_engine):
    repositorio, _ = preparar(database_engine)
    tarde = publicar_evento(
        repositorio, HOJE + timedelta(days=2), CRIADO_EM
    )
    cedo = publicar_evento(
        repositorio, HOJE + timedelta(days=2), CRIADO_EM - timedelta(hours=3)
    )
    perto = publicar_evento(repositorio, HOJE + timedelta(days=1))
    longe = publicar_evento(repositorio, HOJE + timedelta(days=9))

    ids = [
        ad.id for ad in repositorio.listar_eventos_futuros(HOJE, 10)
    ]

    assert ids == [perto.id, cedo.id, tarde.id, longe.id]


def test_destaques_incluem_hoje_e_excluem_dias_passados(database_engine):
    repositorio, _ = preparar(database_engine)
    hoje = publicar_evento(repositorio, HOJE)
    publicar_evento(repositorio, HOJE - timedelta(days=1))

    ids = [ad.id for ad in repositorio.listar_eventos_futuros(HOJE, 10)]

    assert ids == [hoje.id]


def test_destaques_respeitam_o_limite(database_engine):
    repositorio, _ = preparar(database_engine)
    for dia in range(1, 8):
        publicar_evento(repositorio, HOJE + timedelta(days=dia))

    destaques = repositorio.listar_eventos_futuros(HOJE, 5)

    assert [ad.data_evento for ad in destaques] == [
        HOJE + timedelta(days=dia) for dia in range(1, 6)
    ]


def test_destaques_ignoram_vendidos_expirados_produtos_e_prazo_vencido(
    database_engine,
):
    repositorio, session_factory = preparar(database_engine)
    amanha = HOJE + timedelta(days=1)
    vendido = publicar_evento(repositorio, amanha)
    expirado = publicar_evento(repositorio, amanha)
    vencido = publicar_evento(repositorio, amanha)
    valido = publicar_evento(repositorio, amanha)
    repositorio.publish(produto(), "Ana", CRIADO_EM, EXPIRA_EM)
    repositorio.alterar_status(vendido.id, "sold")
    repositorio.alterar_status(expirado.id, "expired")
    with session_factory.begin() as session:
        session.get(AdModel, vencido.id).expires_at = datetime(
            2020, 1, 1, tzinfo=UTC
        )

    ids = [ad.id for ad in repositorio.listar_eventos_futuros(HOJE, 10)]

    assert ids == [valido.id]


def test_destaques_ignoram_eventos_antigos_sem_data(database_engine):
    repositorio, session_factory = preparar(database_engine)
    antigo = publicar_evento(repositorio, HOJE + timedelta(days=1))
    with session_factory.begin() as session:
        session.get(AdModel, antigo.id).data_evento = None

    assert repositorio.listar_eventos_futuros(HOJE, 10) == []


def test_feed_pode_excluir_eventos_e_o_filtro_de_tipo_os_mantem(
    database_engine,
):
    repositorio, _ = preparar(database_engine)
    publicar_evento(repositorio, HOJE + timedelta(days=1))
    livro = repositorio.publish(produto(), "Ana", CRIADO_EM, EXPIRA_EM)

    sem_eventos, total = repositorio.list_published(
        1, 20, None, None, excluir_eventos=True
    )
    so_eventos, total_eventos = repositorio.list_published(
        1, 20, None, "event"
    )
    todos, total_todos = repositorio.list_published(1, 20, None, None)

    assert [ad.id for ad in sem_eventos] == [livro.id]
    assert total == 1
    assert total_eventos == 1
    assert total_todos == 2
    assert [ad.type for ad in so_eventos] == ["event"]


def test_evento_sem_preco_e_gravado_sem_valor_e_sem_a_combinar(
    database_engine,
):
    repositorio, _ = preparar(database_engine)

    publicado = publicar_evento(
        repositorio, HOJE + timedelta(days=1), sem_preco=True
    )
    lido = repositorio.buscar_por_id(publicado.id)

    assert lido.sem_preco is True
    assert lido.price is None
    assert lido.preco_a_combinar is False


def test_atualizar_pode_trocar_sem_preco_por_a_combinar(database_engine):
    repositorio, _ = preparar(database_engine)
    publicado = publicar_evento(
        repositorio, HOJE + timedelta(days=1), sem_preco=True
    )

    editado = repositorio.atualizar(
        publicado.id, evento(HOJE + timedelta(days=1))
    )

    assert editado.sem_preco is False
    assert editado.preco_a_combinar is True


def test_filtro_de_preco_deixa_de_fora_evento_sem_preco(database_engine):
    repositorio, _ = preparar(database_engine)
    publicar_evento(repositorio, HOJE + timedelta(days=1), sem_preco=True)

    itens, total = repositorio.list_published(
        1, 20, None, None, min_price=0
    )

    assert itens == [] and total == 0
