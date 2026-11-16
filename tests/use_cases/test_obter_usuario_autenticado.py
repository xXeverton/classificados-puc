import pytest

from domain.erros import TokenInvalido
from domain.usuario import Vinculo
from infra.repositories.memoria import UsuarioRepositoryMemoria
from tests.fakes import ServicoTokenFalso, criar_usuario
from use_cases.autenticacao import ObterUsuarioAutenticado


@pytest.fixture
def usuarios():
    return UsuarioRepositoryMemoria([criar_usuario()])


@pytest.fixture
def obter(usuarios):
    return ObterUsuarioAutenticado(ServicoTokenFalso(), usuarios)


def test_ca8_token_valido_identifica_o_usuario(obter):
    assert obter.executar("token-1").matricula == "2310001"


def test_ca8_token_invalido_e_recusado(obter):
    with pytest.raises(TokenInvalido):
        obter.executar("lixo")


def test_token_de_usuario_removido_e_recusado(obter):
    with pytest.raises(TokenInvalido):
        obter.executar("token-99")


def test_token_de_usuario_que_perdeu_o_vinculo_e_recusado(usuarios, obter):
    usuarios.adicionar(criar_usuario(vinculo=Vinculo.TERCEIRIZADO))

    with pytest.raises(TokenInvalido):
        obter.executar("token-1")
