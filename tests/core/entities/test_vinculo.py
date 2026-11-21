import pytest

from server.core.entities.vinculo import Vinculo


@pytest.mark.parametrize("valor", ["aluno", "funcionario"])
def test_vinculo_accepts_aluno_and_funcionario(valor):
    assert Vinculo(valor).value == valor


@pytest.mark.parametrize("valor", ["terceirizado", "Aluno", ""])
def test_vinculo_rejects_other_values(valor):
    with pytest.raises(ValueError):
        Vinculo(valor)
