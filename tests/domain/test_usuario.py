import pytest

from domain.usuario import Vinculo
from tests.fakes import criar_usuario


@pytest.mark.parametrize("vinculo", [Vinculo.ALUNO, Vinculo.FUNCIONARIO])
def test_aluno_e_funcionario_podem_acessar(vinculo):
    assert criar_usuario(vinculo=vinculo).pode_acessar()


def test_terceirizado_nao_pode_acessar():
    assert not criar_usuario(vinculo=Vinculo.TERCEIRIZADO).pode_acessar()
