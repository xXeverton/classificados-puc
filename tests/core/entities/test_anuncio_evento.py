"""Event fields of `Anuncio` and the event calendar rules (spec 015)."""

from datetime import UTC, date, datetime, time
from decimal import Decimal

import pytest

from server.core.entities.anuncio import (
    Anuncio,
    LOCAL_EVENTO_MAX_CARACTERES,
)
from server.core.entities.prazo_do_evento import (
    dia_de_hoje,
    fim_do_prazo_do_evento,
)

DIA = date(2026, 12, 5)


def dados(**extras):
    base = {
        "usuario_id": 1,
        "titulo": "Feira de profissões",
        "descricao": "Venha conhecer os cursos.",
        "categoria": "evento",
        "preco": None,
        "data_evento": DIA,
    }
    base.update(extras)
    return base


def test_evento_aceita_so_a_data():
    anuncio = Anuncio(**dados())

    assert anuncio.data_evento == DIA
    assert anuncio.horario_evento is None
    assert anuncio.local_evento is None


def test_evento_aceita_horario_e_local():
    anuncio = Anuncio(
        **dados(horario_evento=time(14, 30), local_evento="Auditório")
    )

    assert anuncio.horario_evento == time(14, 30)
    assert anuncio.local_evento == "Auditório"


@pytest.mark.parametrize("data", [None, "2026-12-05", 20261205])
def test_evento_exige_data_de_verdade(data):
    with pytest.raises(ValueError, match="data_evento"):
        Anuncio(**dados(data_evento=data))


def test_evento_recusa_data_com_horas():
    with pytest.raises(ValueError, match="data_evento"):
        Anuncio(**dados(data_evento=datetime(2026, 12, 5, 10, tzinfo=UTC)))


def test_evento_aceita_local_no_limite_e_recusa_acima():
    Anuncio(**dados(local_evento="a" * LOCAL_EVENTO_MAX_CARACTERES))

    with pytest.raises(ValueError, match="local_evento"):
        Anuncio(**dados(local_evento="a" * (LOCAL_EVENTO_MAX_CARACTERES + 1)))


def test_evento_recusa_local_em_branco():
    with pytest.raises(ValueError, match="local_evento"):
        Anuncio(**dados(local_evento="   "))


@pytest.mark.parametrize(
    "extra",
    [
        {"data_evento": DIA},
        {"horario_evento": time(10, 0)},
        {"local_evento": "Auditório"},
    ],
)
@pytest.mark.parametrize("categoria", ["produto", "servico"])
def test_fora_de_evento_nao_aceita_campos_de_evento(categoria, extra):
    base = {
        "usuario_id": 1,
        "titulo": "Livro de Cálculo",
        "descricao": "Livro em bom estado.",
        "categoria": categoria,
        "preco": Decimal("10"),
        "estado_conservacao": "novo" if categoria == "produto" else None,
    }

    with pytest.raises(ValueError, match="evento"):
        Anuncio(**base, **extra)


def test_dia_de_hoje_segue_brasilia_e_nao_o_utc():
    # 02:00 UTC de 5/12 ainda é 4/12 às 23:00 em Brasília.
    agora = datetime(2026, 12, 5, 2, 0, tzinfo=UTC)

    assert dia_de_hoje(agora) == date(2026, 12, 4)


def test_dia_de_hoje_no_meio_do_dia():
    assert dia_de_hoje(datetime(2026, 12, 5, 15, 0, tzinfo=UTC)) == DIA


def test_fim_do_prazo_e_o_inicio_do_dia_seguinte_em_brasilia():
    fim = fim_do_prazo_do_evento(DIA)

    assert fim == datetime(2026, 12, 6, 3, 0, tzinfo=UTC)


def test_evento_ainda_vale_no_ultimo_minuto_do_dia_do_evento():
    fim = fim_do_prazo_do_evento(DIA)
    ultimo_minuto = datetime(2026, 12, 6, 2, 59, tzinfo=UTC)

    assert dia_de_hoje(ultimo_minuto) == DIA
    assert ultimo_minuto < fim


def test_evento_pode_ficar_sem_preco():
    anuncio = Anuncio(**dados(sem_preco=True))

    assert anuncio.sem_preco is True
    assert anuncio.preco is None


def test_sem_preco_nao_aceita_valor():
    with pytest.raises(ValueError, match="sem_preco"):
        Anuncio(**dados(sem_preco=True, preco=Decimal("10")))


@pytest.mark.parametrize("categoria", ["produto", "servico"])
def test_so_evento_pode_ficar_sem_preco(categoria):
    with pytest.raises(ValueError, match="sem_preco"):
        Anuncio(
            usuario_id=1,
            titulo="Livro de Cálculo",
            descricao="Livro em bom estado.",
            categoria=categoria,
            preco=None,
            estado_conservacao="novo" if categoria == "produto" else None,
            sem_preco=True,
        )
