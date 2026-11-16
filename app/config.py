"""Configuração da aplicação lida de variáveis de ambiente."""

import os

PADROES = {
    "JWT_SECRET": "",
    "JWT_EXPIRA_MINUTOS": 60,
    "URL_LINK_MAGICO": "http://localhost:5000/entrar/link",
    "SMTP_HOST": "",
    "SMTP_PORT": 587,
    "SMTP_USUARIO": "",
    "SMTP_SENHA": "",
    "SMTP_REMETENTE": "nao-responda@localhost",
    "SMTP_STARTTLS": True,
}

_VALORES_VERDADEIROS = {"1", "true", "sim", "yes"}


def _converter(valor_texto: str, padrao):
    if isinstance(padrao, bool):
        return valor_texto.strip().lower() in _VALORES_VERDADEIROS
    if isinstance(padrao, int):
        return int(valor_texto)
    return valor_texto


def carregar_config(sobrescritas: dict | None = None) -> dict:
    """Junta padrões, variáveis de ambiente e sobrescritas (nessa ordem)."""
    config = {}
    for chave, padrao in PADROES.items():
        valor_ambiente = os.environ.get(chave)
        config[chave] = (
            padrao
            if valor_ambiente is None
            else _converter(valor_ambiente, padrao)
        )
    config.update(sobrescritas or {})
    return config
