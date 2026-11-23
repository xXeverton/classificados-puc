"""Featured events and the event rules of publish, edit and renew (015)."""

from datetime import UTC, date, datetime, timedelta
from decimal import Decimal

import pytest

from server.core.entities.ad import Ad
from server.core.entities.anunciante import Anunciante
from server.core.entities.anuncio import Anuncio
from server.core.entities.contato import Contato
from server.core.entities.usuario import Usuario
from server.core.interfaces.ad_repository_interface import AdRepository
from server.core.interfaces.eventos_em_destaque_repository_interface import (
    EventosEmDestaqueRepository,
)
from server.core.usecases.editar_anuncio import EditarAnuncio
from server.core.usecases.erros import (
    DataDeEventoInvalida,
    EventoNaoRenovavel,
    UsuarioNaoAutenticado,
)
from server.core.usecases.listar_eventos_em_destaque import (
    LIMITE_EVENTOS_EM_DESTAQUE,
    ListarEventosEmDestaque,
)
from server.core.usecases.publicar_anuncio import PublicarAnuncio
from server.core.usecases.renovar_anuncio import RenovarAnuncio
from tests.core.usecases.fakes import (
    AnuncianteRepositoryEmMemoria,
    RelogioFalso,
)
from tests.core.usecases.test_gerenciar_anuncio import (
    AnuncioEditavelRepositoryEmMemoria,
    DONO,
)

# 12:00 UTC de 20/11/2026 é 09:00 em Brasília, ainda dia 20.
AGORA = datetime(2026, 11, 20, 12, 0, tzinfo=UTC)
HOJE = date(2026, 11, 20)


def evento_salvo(ad_id, data_evento, **extras):
    dados = {
        "id": ad_id,
        "title": f"Evento {ad_id}",
        "description": "Venha participar.",
        "type": "event",
        "category": "evento",
        "price": None,
        "preco_a_combinar": True,
        "created_at": AGORA - timedelta(days=ad_id),
        "status": "published",
        "expires_at": AGORA + timedelta(days=10),
        "usuario_id": DONO,
        "data_evento": data_evento,
    }
    dados.update(extras)
    return Ad(**dados)


class EventosEmMemoria(EventosEmDestaqueRepository):
    """Same selection rule the SQL gateway applies."""

    def __init__(self, anuncios):
        self.anuncios = anuncios
        self.consultas = []

    def listar_eventos_futuros(self, a_partir_de, limite):
        self.consultas.append((a_partir_de, limite))
        eventos = [
            ad
            for ad in self.anuncios
            if ad.status == "published"
            and ad.type == "event"
            and ad.data_evento is not None
            and ad.data_evento >= a_partir_de
        ]
        eventos.sort(key=lambda ad: (ad.data_evento, ad.created_at, ad.id))
        return eventos[:limite]


def usuario():
    return Usuario(
        nome="Ana",
        email="ana@aluno.puc-rio.br",
        nome_usuario="ana123",
        vinculo="aluno",
        senha_hash="hash",
        id=DONO,
        confirmado_em=AGORA,
    )


def listar(anuncios, agora=AGORA):
    repositorio = EventosEmMemoria(anuncios)
    caso = ListarEventosEmDestaque(repositorio, RelogioFalso(agora))
    return caso.executar(usuario()), repositorio


def test_destaques_pedem_ao_repositorio_o_dia_de_hoje_em_brasilia_e_o_limite():
    _, repositorio = listar([], AGORA.replace(hour=2))

    assert repositorio.consultas == [
        (date(2026, 11, 19), LIMITE_EVENTOS_EM_DESTAQUE)
    ]


def test_destaques_limitam_a_cinco_pelos_mais_proximos():
    anuncios = [
        evento_salvo(i, HOJE + timedelta(days=i)) for i in range(1, 8)
    ]

    destaques, _ = listar(anuncios)

    assert len(destaques) == LIMITE_EVENTOS_EM_DESTAQUE == 5
    assert [ad.id for ad in destaques] == [1, 2, 3, 4, 5]


def test_destaques_em_empate_de_data_vem_o_publicado_primeiro():
    dia = HOJE + timedelta(days=3)
    anuncios = [
        evento_salvo(1, dia, created_at=AGORA - timedelta(hours=1)),
        evento_salvo(2, dia, created_at=AGORA - timedelta(hours=5)),
    ]

    destaques, _ = listar(anuncios)

    assert [ad.id for ad in destaques] == [2, 1]


def test_evento_de_hoje_continua_nos_destaques():
    destaques, _ = listar([evento_salvo(1, HOJE)])

    assert [ad.id for ad in destaques] == [1]


def test_evento_de_ontem_nao_aparece():
    destaques, _ = listar([evento_salvo(1, HOJE - timedelta(days=1))])

    assert destaques == []


def test_destaques_ignoram_expirados_vendidos_e_sem_data_e_produtos():
    amanha = HOJE + timedelta(days=1)
    anuncios = [
        evento_salvo(1, amanha, status="expired"),
        evento_salvo(2, amanha, status="sold"),
        evento_salvo(3, None),
        evento_salvo(4, amanha, type="product", category="produto"),
        evento_salvo(5, amanha),
    ]

    destaques, _ = listar(anuncios)

    assert [ad.id for ad in destaques] == [5]


def test_destaques_sem_eventos_devolvem_lista_vazia():
    destaques, _ = listar([])

    assert destaques == []


def test_destaques_exigem_usuario():
    caso = ListarEventosEmDestaque(EventosEmMemoria([]), RelogioFalso(AGORA))

    with pytest.raises(UsuarioNaoAutenticado):
        caso.executar(None)


# ---- Publicar


class AdRepositoryQuePublica(AdRepository):
    def __init__(self):
        self.publicados = []

    def publish(self, anuncio, nome_anunciante, criado_em, expira_em):
        self.publicados.append((anuncio, criado_em, expira_em))
        return Ad(
            id=1,
            title=anuncio.titulo,
            description=anuncio.descricao,
            type="event" if anuncio.categoria == "evento" else "product",
            category=anuncio.categoria,
            price=None,
            created_at=criado_em,
            status="published",
            expires_at=expira_em,
            data_evento=anuncio.data_evento,
            horario_evento=anuncio.horario_evento,
            local_evento=anuncio.local_evento,
        )

    def buscar_por_id(self, anuncio_id):
        raise NotImplementedError

    def list_published(self, *args, **kwargs):
        raise NotImplementedError


def publicador(agora=AGORA):
    anunciantes = AnuncianteRepositoryEmMemoria()
    anunciantes.salvar(
        Anunciante(
            usuario_id=DONO,
            nome_exibicao="Ana",
            contatos=(Contato.criar("email", "ana@example.com"),),
        )
    )
    repositorio = AdRepositoryQuePublica()
    return (
        PublicarAnuncio(repositorio, anunciantes, RelogioFalso(agora)),
        repositorio,
    )


def evento_para_publicar(data_evento, **extras):
    dados = {
        "usuario_id": DONO,
        "titulo": "Feira de profissões",
        "descricao": "Venha conhecer os cursos.",
        "categoria": "evento",
        "preco": None,
        "data_evento": data_evento,
    }
    dados.update(extras)
    return Anuncio(**dados)


def test_publicar_evento_expira_no_dia_seguinte_ao_evento():
    caso, repositorio = publicador()
    data = HOJE + timedelta(days=60)

    publicado = caso.executar(evento_para_publicar(data))

    # Mais de 30 dias à frente: o prazo segue o evento, não os 30 dias.
    assert publicado.expires_at == datetime(2027, 1, 20, 3, 0, tzinfo=UTC)
    assert repositorio.publicados[0][2] == publicado.expires_at


def test_publicar_evento_de_hoje_e_aceito():
    caso, _ = publicador()

    publicado = caso.executar(evento_para_publicar(HOJE))

    assert publicado.expires_at == datetime(2026, 11, 21, 3, 0, tzinfo=UTC)


def test_publicar_evento_com_data_passada_falha_e_nao_grava():
    caso, repositorio = publicador()

    with pytest.raises(DataDeEventoInvalida):
        caso.executar(evento_para_publicar(HOJE - timedelta(days=1)))

    assert repositorio.publicados == []


def test_publicar_evento_as_23h_de_brasilia_ainda_conta_o_dia_local():
    # 02:00 UTC de 21/11 ainda é 20/11 em Brasília.
    caso, _ = publicador(datetime(2026, 11, 21, 2, 0, tzinfo=UTC))

    publicado = caso.executar(evento_para_publicar(HOJE))

    assert publicado.data_evento == HOJE


def test_publicar_produto_mantem_o_prazo_de_30_dias():
    caso, _ = publicador()
    produto = Anuncio(
        usuario_id=DONO,
        titulo="Livro de Cálculo",
        descricao="Livro em bom estado.",
        categoria="produto",
        preco=Decimal("10"),
        estado_conservacao="novo",
    )

    publicado = caso.executar(produto)

    assert publicado.expires_at == AGORA + timedelta(days=30)


# ---- Editar


def editor(anuncios, agora=AGORA):
    repositorio = AnuncioEditavelRepositoryEmMemoria(anuncios)
    return EditarAnuncio(repositorio, RelogioFalso(agora)), repositorio


def edicao_de_evento(data_evento):
    return evento_para_publicar(data_evento)


def test_editar_data_do_evento_recalcula_o_prazo():
    caso, _ = editor([evento_salvo(1, HOJE + timedelta(days=5))])

    editado = caso.executar(1, edicao_de_evento(HOJE + timedelta(days=40)))

    assert editado.expires_at == datetime(2026, 12, 31, 3, 0, tzinfo=UTC)
    assert editado.status == "published"


def test_editar_evento_com_data_passada_falha():
    original = evento_salvo(1, HOJE + timedelta(days=5))
    caso, repositorio = editor([original])

    with pytest.raises(DataDeEventoInvalida):
        caso.executar(1, edicao_de_evento(HOJE - timedelta(days=1)))

    assert repositorio.anuncios[1] == original


def test_editar_evento_expirado_com_nova_data_publica_de_novo():
    caso, _ = editor(
        [evento_salvo(1, HOJE - timedelta(days=3), status="expired")]
    )

    editado = caso.executar(1, edicao_de_evento(HOJE + timedelta(days=2)))

    assert editado.status == "published"
    assert editado.expires_at == datetime(2026, 11, 23, 3, 0, tzinfo=UTC)


def test_editar_evento_vendido_mantem_situacao_e_prazo():
    original = evento_salvo(1, HOJE + timedelta(days=5), status="sold")
    caso, _ = editor([original])

    editado = caso.executar(1, edicao_de_evento(HOJE + timedelta(days=9)))

    assert editado.status == "sold"
    assert editado.expires_at == original.expires_at


# ---- Renovar


def test_evento_nao_e_renovavel_mesmo_expirado():
    repositorio = AnuncioEditavelRepositoryEmMemoria(
        [evento_salvo(1, HOJE - timedelta(days=1), status="expired")]
    )

    with pytest.raises(EventoNaoRenovavel):
        RenovarAnuncio(repositorio, RelogioFalso(AGORA)).executar(1, DONO)

    assert repositorio.anuncios[1].status == "expired"
