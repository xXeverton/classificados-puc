"""HTTP contract of events and the home highlights (spec 015)."""

from datetime import date, datetime, timedelta, timezone

import pytest

from tests.api.test_ads_controller import (
    complete_advertiser_profile,
    create_ads_app,
)


def dia(dias_a_frente):
    return (date.today() + timedelta(days=dias_a_frente)).isoformat()


def corpo_do_evento(**extras):
    corpo = {
        "titulo": "Feira de profissões",
        "categoria": "evento",
        "descricao": "Venha conhecer os cursos.",
        "preco_a_combinar": True,
        "data_evento": dia(3),
    }
    corpo.update(extras)
    return corpo


@pytest.fixture
def ambiente():
    app = create_ads_app()
    complete_advertiser_profile(app)
    yield app, app.test_client(), app.extensions["test_auth_headers"]
    app.extensions["database_engine"].dispose()


def publicar(cliente, headers, **extras):
    return cliente.post(
        "/api/ads", json=corpo_do_evento(**extras), headers=headers
    )


def destaques(cliente, headers):
    resposta = cliente.get("/api/eventos-destaque", headers=headers)
    assert resposta.status_code == 200
    return resposta.json["items"]


def test_destaques_exigem_sessao():
    app = create_ads_app()

    resposta = app.test_client().get("/api/eventos-destaque")

    assert resposta.status_code == 401
    app.extensions["database_engine"].dispose()


def test_destaques_vazios_quando_nao_ha_eventos_com_data(ambiente):
    _, cliente, headers = ambiente

    assert destaques(cliente, headers) == []


def test_publicar_evento_devolve_data_horario_e_local(ambiente):
    _, cliente, headers = ambiente

    resposta = publicar(
        cliente,
        headers,
        horario_evento="19:30",
        local_evento="  Auditório Padre Anchieta  ",
    )

    assert resposta.status_code == 201
    assert resposta.json["data_evento"] == dia(3)
    assert resposta.json["horario_evento"] == "19:30"
    assert resposta.json["local_evento"] == "Auditório Padre Anchieta"
    assert resposta.json["type"] == "event"


def test_evento_publicado_aparece_nos_destaques(ambiente):
    _, cliente, headers = ambiente
    id_publicado = publicar(cliente, headers).json["id"]

    itens = destaques(cliente, headers)

    assert [item["id"] for item in itens] == [id_publicado]
    assert itens[0]["title"] == "Feira de profissões"
    assert itens[0]["data_evento"] == dia(3)


def test_destaques_mostram_no_maximo_cinco_pelos_mais_proximos(ambiente):
    _, cliente, headers = ambiente
    for dias in (9, 2, 7, 3, 8, 4, 5):
        publicar(
            cliente, headers, titulo=f"Evento em {dias} dias",
            data_evento=dia(dias),
        )

    itens = destaques(cliente, headers)

    assert [item["data_evento"] for item in itens] == [
        dia(dias) for dias in (2, 3, 4, 5, 7)
    ]


def test_evento_publicado_para_hoje_aparece_nos_destaques(ambiente):
    _, cliente, headers = ambiente
    hoje = (datetime.now(timezone.utc) - timedelta(hours=3)).date()
    hoje = hoje.isoformat()

    resposta = publicar(cliente, headers, data_evento=hoje)

    assert resposta.status_code == 201
    assert [i["id"] for i in destaques(cliente, headers)] == [
        resposta.json["id"]
    ]


@pytest.mark.parametrize(
    ("extras", "campo"),
    [
        ({"data_evento": None}, "data_evento"),
        ({"data_evento": ""}, "data_evento"),
        ({"data_evento": "05/12/2026"}, "data_evento"),
        ({"data_evento": "2026-02-30"}, "data_evento"),
        ({"data_evento": 20261205}, "data_evento"),
        ({"data_evento": "2020-01-01"}, "data_evento"),
        ({"horario_evento": "25:00"}, "horario_evento"),
        ({"horario_evento": "9h"}, "horario_evento"),
        ({"local_evento": "a" * 81}, "local_evento"),
        ({"local_evento": "   "}, "local_evento"),
    ],
)
def test_publicar_evento_com_dados_invalidos_nao_publica(
    ambiente, extras, campo
):
    app, cliente, headers = ambiente
    antes = len(cliente.get("/api/ads", headers=headers).json["items"])

    resposta = publicar(cliente, headers, **extras)

    assert resposta.status_code == 422
    assert campo in resposta.json["campos"]
    depois = len(cliente.get("/api/ads", headers=headers).json["items"])
    assert depois == antes


@pytest.mark.parametrize(
    "campo",
    ["data_evento", "horario_evento", "local_evento"],
)
def test_campos_de_evento_nao_valem_para_produto(ambiente, campo):
    _, cliente, headers = ambiente
    valores = {
        "data_evento": dia(3),
        "horario_evento": "10:00",
        "local_evento": "Auditório",
    }

    resposta = cliente.post(
        "/api/ads",
        json={
            "titulo": "Livro de Cálculo",
            "categoria": "produto",
            "estado_conservacao": "novo",
            "descricao": "Livro em bom estado.",
            "preco": "40",
            campo: valores[campo],
        },
        headers=headers,
    )

    assert resposta.status_code == 422
    assert campo in resposta.json["campos"]


def test_publicar_evento_por_formulario_multipart_aceita_campos_vazios(
    ambiente,
):
    _, cliente, headers = ambiente

    resposta = cliente.post(
        "/api/ads",
        data=corpo_do_evento(
            preco_a_combinar="true", horario_evento="", local_evento=""
        ),
        content_type="multipart/form-data",
        headers=headers,
    )

    assert resposta.status_code == 201
    assert resposta.json["horario_evento"] is None
    assert resposta.json["local_evento"] is None


def test_feed_sem_filtro_pode_excluir_eventos(ambiente):
    _, cliente, headers = ambiente
    publicar(cliente, headers)

    todos = cliente.get("/api/ads", headers=headers).json["items"]
    sem_eventos = cliente.get(
        "/api/ads", query_string={"excluir_eventos": "true"}, headers=headers
    ).json["items"]
    so_eventos = cliente.get(
        "/api/ads", query_string={"type": "event"}, headers=headers
    ).json["items"]

    assert any(item["type"] == "event" for item in todos)
    assert all(item["type"] != "event" for item in sem_eventos)
    assert len(sem_eventos) < len(todos)
    assert any(item["title"] == "Feira de profissões" for item in so_eventos)


def test_detalhes_do_evento_mostram_data_horario_e_local(ambiente):
    _, cliente, headers = ambiente
    id_publicado = publicar(
        cliente, headers, horario_evento="08:00", local_evento="Pátio"
    ).json["id"]

    resposta = cliente.get(f"/api/ads/{id_publicado}", headers=headers)

    assert resposta.status_code == 200
    anuncio = resposta.json["ad"]
    assert anuncio["data_evento"] == dia(3)
    assert anuncio["horario_evento"] == "08:00"
    assert anuncio["local_evento"] == "Pátio"


def test_editar_evento_troca_a_data_e_move_o_prazo(ambiente):
    _, cliente, headers = ambiente
    publicado = publicar(cliente, headers).json

    resposta = cliente.put(
        f"/api/ads/{publicado['id']}",
        json=corpo_do_evento(data_evento=dia(40), local_evento="Pátio"),
        headers=headers,
    )

    assert resposta.status_code == 200
    assert resposta.json["data_evento"] == dia(40)
    assert resposta.json["local_evento"] == "Pátio"
    assert resposta.json["expires_at"] > publicado["expires_at"]


def test_editar_evento_com_data_passada_falha(ambiente):
    _, cliente, headers = ambiente
    id_publicado = publicar(cliente, headers).json["id"]

    resposta = cliente.put(
        f"/api/ads/{id_publicado}",
        json=corpo_do_evento(data_evento="2020-01-01"),
        headers=headers,
    )

    assert resposta.status_code == 422
    assert "data_evento" in resposta.json["campos"]
    assert destaques(cliente, headers)[0]["data_evento"] == dia(3)


def test_evento_nao_pode_ser_renovado(ambiente):
    _, cliente, headers = ambiente
    id_publicado = publicar(cliente, headers).json["id"]

    resposta = cliente.post(
        f"/api/ads/{id_publicado}/renovar", headers=headers
    )

    assert resposta.status_code == 422
    assert resposta.json["code"] == "evento_nao_renovavel"


def test_evento_pode_ser_publicado_sem_preco(ambiente):
    _, cliente, headers = ambiente

    resposta = cliente.post(
        "/api/ads",
        json=corpo_do_evento(preco_a_combinar=False, sem_preco=True),
        headers=headers,
    )

    assert resposta.status_code == 201
    assert resposta.json["sem_preco"] is True
    assert resposta.json["price"] is None
    assert resposta.json["preco_a_combinar"] is False
    itens = destaques(cliente, headers)
    assert itens[0]["sem_preco"] is True


def test_sem_preco_aceita_formulario_multipart(ambiente):
    _, cliente, headers = ambiente
    corpo = corpo_do_evento(sem_preco="true", preco_a_combinar="false")

    resposta = cliente.post(
        "/api/ads",
        data=corpo,
        content_type="multipart/form-data",
        headers=headers,
    )

    assert resposta.status_code == 201
    assert resposta.json["sem_preco"] is True


@pytest.mark.parametrize(
    ("extras", "campo"),
    [
        ({"preco_a_combinar": True}, "sem_preco"),
        ({"preco": "10"}, "preco"),
        ({"sem_preco": "sim"}, "sem_preco"),
    ],
)
def test_sem_preco_recusa_combinacoes_invalidas(ambiente, extras, campo):
    _, cliente, headers = ambiente
    corpo = corpo_do_evento(preco_a_combinar=False, sem_preco=True)
    corpo.update(extras)

    resposta = cliente.post("/api/ads", json=corpo, headers=headers)

    assert resposta.status_code == 422
    assert campo in resposta.json["campos"]


def test_so_evento_pode_ficar_sem_preco(ambiente):
    _, cliente, headers = ambiente

    resposta = cliente.post(
        "/api/ads",
        json={
            "titulo": "Livro de Cálculo",
            "categoria": "produto",
            "estado_conservacao": "novo",
            "descricao": "Livro em bom estado.",
            "preco_a_combinar": False,
            "sem_preco": True,
        },
        headers=headers,
    )

    assert resposta.status_code == 422
    assert "sem_preco" in resposta.json["campos"]


def test_editar_evento_de_sem_preco_para_preco_informado(ambiente):
    _, cliente, headers = ambiente
    id_publicado = cliente.post(
        "/api/ads",
        json=corpo_do_evento(preco_a_combinar=False, sem_preco=True),
        headers=headers,
    ).json["id"]

    resposta = cliente.put(
        f"/api/ads/{id_publicado}",
        json=corpo_do_evento(preco_a_combinar=False, preco="15,50"),
        headers=headers,
    )

    assert resposta.status_code == 200
    assert resposta.json["sem_preco"] is False
    assert resposta.json["price"] == 15.5
