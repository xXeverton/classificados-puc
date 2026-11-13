from datetime import timedelta

from domain.autenticacao import LinkMagico, PoliticaBloqueio, TentativasLogin
from tests.fakes import INSTANTE_INICIAL

POLITICA = PoliticaBloqueio()


def registrar_falhas(quantidade, agora=INSTANTE_INICIAL):
    tentativas = TentativasLogin()
    for _ in range(quantidade):
        tentativas = tentativas.registrar_falha(agora, POLITICA)
    return tentativas


def test_politica_padrao_bloqueia_5_tentativas_por_10_minutos():
    assert POLITICA.max_tentativas == 5
    assert POLITICA.duracao == timedelta(minutes=10)


def test_quatro_falhas_nao_bloqueiam():
    tentativas = registrar_falhas(4)

    assert tentativas.falhas_consecutivas == 4
    assert not tentativas.esta_bloqueado(INSTANTE_INICIAL)


def test_quinta_falha_bloqueia_por_10_minutos():
    tentativas = registrar_falhas(5)

    assert tentativas.bloqueado_ate == INSTANTE_INICIAL + timedelta(minutes=10)
    assert tentativas.esta_bloqueado(
        INSTANTE_INICIAL + timedelta(minutes=9, seconds=59)
    )
    assert not tentativas.esta_bloqueado(
        INSTANTE_INICIAL + timedelta(minutes=10)
    )


def test_falha_depois_do_bloqueio_recomeca_a_contagem():
    depois_do_bloqueio = INSTANTE_INICIAL + timedelta(minutes=11)

    tentativas = registrar_falhas(5).registrar_falha(
        depois_do_bloqueio, POLITICA
    )

    assert tentativas.falhas_consecutivas == 1
    assert not tentativas.esta_bloqueado(depois_do_bloqueio)


def criar_link(**sobrescritas):
    dados = {
        "token_hash": "abc",
        "usuario_id": 1,
        "expira_em": INSTANTE_INICIAL + timedelta(minutes=15),
    }
    dados.update(sobrescritas)
    return LinkMagico(**dados)


def test_link_dentro_da_validade_pode_ser_usado():
    assert criar_link().pode_ser_usado(INSTANTE_INICIAL)


def test_link_expirado_nao_pode_ser_usado():
    assert not criar_link().pode_ser_usado(
        INSTANTE_INICIAL + timedelta(minutes=15)
    )


def test_link_usado_nao_pode_ser_reutilizado():
    assert not criar_link(usado=True).pode_ser_usado(INSTANTE_INICIAL)
