"""Regra dos e-mails aceitos na plataforma (RN2)."""

from domain.erros import EmailNaoInstitucional

DOMINIOS_INSTITUCIONAIS = frozenset({"aluno.puc-rio.br", "puc-rio.br"})


def validar_email_institucional(email: str) -> str:
    """Retorna o e-mail normalizado ou levanta `EmailNaoInstitucional`.

    Só os domínios exatos são aceitos; subdomínios ficam de fora.
    """
    normalizado = email.strip().lower()
    usuario, separador, dominio = normalizado.rpartition("@")
    if not separador or not usuario or "@" in usuario:
        raise EmailNaoInstitucional()
    if dominio not in DOMINIOS_INSTITUCIONAIS:
        raise EmailNaoInstitucional()
    return normalizado
