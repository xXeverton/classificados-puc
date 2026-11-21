from datetime import timedelta

import pytest

from server.core.usecases.erros import TokenExpirado, TokenInvalido


def test_valid_link_confirms_account(ambiente):
    usuario = ambiente.cadastrar_ana()
    ambiente.relogio.avancar(timedelta(minutes=15))

    confirmado = ambiente.confirmar.executar(ambiente.enviador.ultimo.token)

    assert confirmado.id == usuario.id
    assert confirmado.esta_confirmado()
    assert ambiente.usuarios.buscar_por_id(usuario.id).esta_confirmado()


def test_link_older_than_fifteen_minutes_is_expired(ambiente):
    usuario = ambiente.cadastrar_ana()
    ambiente.relogio.avancar(timedelta(minutes=15, seconds=1))

    with pytest.raises(TokenExpirado):
        ambiente.confirmar.executar(ambiente.enviador.ultimo.token)

    assert not ambiente.usuarios.buscar_por_id(usuario.id).esta_confirmado()


def test_link_cannot_be_used_twice(ambiente):
    ambiente.cadastrar_ana()
    token = ambiente.enviador.ultimo.token
    ambiente.confirmar.executar(token)

    with pytest.raises(TokenInvalido):
        ambiente.confirmar.executar(token)


def test_unknown_link_is_rejected(ambiente):
    with pytest.raises(TokenInvalido):
        ambiente.confirmar.executar("inexistente")
