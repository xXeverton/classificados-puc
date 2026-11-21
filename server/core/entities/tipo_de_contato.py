"""Kinds of contact an advertiser can offer to buyers."""

from enum import Enum


class TipoDeContato(Enum):
    WHATSAPP = "whatsapp"
    TELEFONE = "telefone"
    EMAIL = "email"
    SITE = "site"
    LINK = "link"
