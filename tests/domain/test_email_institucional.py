import pytest

from domain.email_institucional import validar_email_institucional
from domain.erros import EmailNaoInstitucional


@pytest.mark.parametrize(
    "email",
    ["ana@aluno.puc-rio.br", "joao.silva@puc-rio.br"],
)
def test_aceita_dominios_institucionais(email):
    assert validar_email_institucional(email) == email


def test_normaliza_maiusculas_e_espacos():
    assert (
        validar_email_institucional("  Ana@ALUNO.PUC-Rio.br ")
        == "ana@aluno.puc-rio.br"
    )


@pytest.mark.parametrize(
    "email",
    [
        "ana@gmail.com",
        "ana@ccc.puc-rio.br",
        "ana@puc-rio.br.com",
        "ana@fakepuc-rio.br",
        "ana@aluno.puc-rio.br@gmail.com",
        "@puc-rio.br",
        "puc-rio.br",
        "",
    ],
)
def test_recusa_email_fora_dos_dominios(email):
    with pytest.raises(EmailNaoInstitucional):
        validar_email_institucional(email)
