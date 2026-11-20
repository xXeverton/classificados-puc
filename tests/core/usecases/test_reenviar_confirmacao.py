import pytest

from server.core.usecases.erros import TokenInvalido


def test_pending_account_receives_new_link_and_old_one_stops_working(
    ambiente,
):
    ambiente.cadastrar_ana()
    antigo = ambiente.enviador.ultimo.token

    ambiente.reenviar.executar(" ANA@aluno.puc-rio.br ")

    novo = ambiente.enviador.ultimo.token
    assert novo != antigo
    with pytest.raises(TokenInvalido):
        ambiente.confirmar.executar(antigo)
    assert ambiente.confirmar.executar(novo).esta_confirmado()


def test_unknown_email_sends_nothing_and_raises_nothing(ambiente):
    ambiente.reenviar.executar("ninguem@aluno.puc-rio.br")

    assert ambiente.enviador.enviados == []


def test_confirmed_account_sends_nothing_and_raises_nothing(ambiente):
    ambiente.cadastrar_confirmado()
    enviados = len(ambiente.enviador.enviados)

    ambiente.reenviar.executar("ana@aluno.puc-rio.br")

    assert len(ambiente.enviador.enviados) == enviados
