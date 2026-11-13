from datetime import timedelta

import jwt
import pytest

from domain.erros import TokenInvalido
from infra.relogio_sistema import RelogioSistema
from infra.seguranca.servico_token_jwt import ServicoTokenJwt
from infra.seguranca.verificador_senha_werkzeug import (
    VerificadorSenhaWerkzeug,
)
from tests.fakes import RelogioControlado

SEGREDO = "segredo-de-teste-com-tamanho-suficiente"
VALIDADE = timedelta(hours=1)


@pytest.fixture
def servico():
    return ServicoTokenJwt(SEGREDO, VALIDADE, RelogioSistema())


def test_token_emitido_e_validado_com_o_mesmo_usuario(servico):
    sessao = servico.emitir(42)

    assert servico.validar(sessao.token) == 42
    assert sessao.expira_em_segundos == 3600


def test_token_expirado_e_recusado():
    relogio = RelogioControlado(RelogioSistema().agora() - timedelta(hours=2))
    token = ServicoTokenJwt(SEGREDO, VALIDADE, relogio).emitir(42).token

    with pytest.raises(TokenInvalido):
        ServicoTokenJwt(SEGREDO, VALIDADE, RelogioSistema()).validar(token)


def test_token_assinado_com_outro_segredo_e_recusado(servico):
    outro = ServicoTokenJwt(
        "outro-segredo-com-tamanho-suficiente!!", VALIDADE, RelogioSistema()
    )

    with pytest.raises(TokenInvalido):
        servico.validar(outro.emitir(42).token)


def test_token_sem_assinatura_e_recusado(servico):
    agora = RelogioSistema().agora()
    token = jwt.encode(
        {"sub": "42", "tipo": "acesso", "iat": agora,
         "exp": agora + VALIDADE},
        key=None,
        algorithm="none",
    )

    with pytest.raises(TokenInvalido):
        servico.validar(token)


def test_token_de_outro_tipo_e_recusado(servico):
    agora = RelogioSistema().agora()
    token = jwt.encode(
        {"sub": "42", "tipo": "outro", "iat": agora,
         "exp": agora + VALIDADE},
        SEGREDO,
        algorithm="HS256",
    )

    with pytest.raises(TokenInvalido):
        servico.validar(token)


def test_texto_qualquer_e_recusado(servico):
    with pytest.raises(TokenInvalido):
        servico.validar("nao-e-um-jwt")


def test_segredo_vazio_e_rejeitado():
    with pytest.raises(ValueError):
        ServicoTokenJwt("", VALIDADE, RelogioSistema())


def test_senha_e_armazenada_como_hash_e_verificada():
    verificador = VerificadorSenhaWerkzeug()
    senha_hash = verificador.gerar_hash("minha-senha")

    assert senha_hash != "minha-senha"
    assert verificador.verificar("minha-senha", senha_hash)
    assert not verificador.verificar("outra-senha", senha_hash)
