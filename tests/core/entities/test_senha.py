import pytest

from server.core.entities.senha import TAMANHO_MINIMO_SENHA, validar_senha


def test_minimum_password_length_is_eight():
    assert TAMANHO_MINIMO_SENHA == 8


def test_validar_senha_rejects_seven_characters():
    with pytest.raises(ValueError, match="8 caracteres"):
        validar_senha("1234567")


def test_validar_senha_accepts_eight_characters():
    validar_senha("12345678")
