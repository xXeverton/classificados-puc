import pytest

from server.core.entities.usuario import Usuario


@pytest.mark.parametrize(
    "email",
    [
        "ana@aluno.puc-rio.br",
        "ana.silva+teste@aluno.puc-rio.br",
        "funcionario@puc-rio.br",
        "ANA@ALUNO.PUC-RIO.BR",
    ],
)
def test_usuario_accepts_valid_institutional_emails(email):
    usuario = Usuario(
        nome="Ana",
        email=email,
        matricula="123",
        vinculo="aluno",
    )

    assert usuario.email == email


@pytest.mark.parametrize(
    "email",
    [
        "",
        "@aluno.puc-rio.br",
        "ana..silva@aluno.puc-rio.br",
        "ana@sub.aluno.puc-rio.br",
        "ana@aluno.puc-rio.br.example.com",
        "ana@gmail.com",
        " ana@puc-rio.br",
    ],
)
def test_usuario_rejects_invalid_or_non_institutional_emails(email):
    with pytest.raises(ValueError):
        Usuario(
            nome="Ana",
            email=email,
            matricula="123",
            vinculo="aluno",
        )
