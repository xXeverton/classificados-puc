"""A way for buyers to reach an advertiser (WhatsApp, phone, e-mail, ...)."""

import re
from dataclasses import dataclass
from urllib.parse import SplitResult, urlsplit

from server.core.entities.politicas_perfil import (
    HOSTS_LINK_WHATSAPP,
    MAXIMO_CARACTERES_ENDERECO,
    MAXIMO_CARACTERES_ROTULO,
    MAXIMO_DIGITOS_CODIGO_PAIS,
    MAXIMO_DIGITOS_TELEFONE,
    MINIMO_DIGITOS_TELEFONE,
)
from server.core.entities.tipo_de_contato import TipoDeContato

_SEPARADORES_DE_TELEFONE = re.compile(r"[\s().+\-]")
_SO_DIGITOS = re.compile(r"[0-9]+")
_EMAIL_PATTERN = re.compile(r"[^@\s]+@[^@\s]+\.[^@\s]+")
_ESQUEMA_HTTPS = "https"
_URL_BASE_CONVERSA = "https://wa.me/"

_TIPOS_COM_CODIGO_DO_PAIS = (TipoDeContato.WHATSAPP, TipoDeContato.TELEFONE)

_MENSAGEM_LINK_DO_WHATSAPP = (
    "Informe um link de conversa do WhatsApp "
    "(https://wa.me/... ou https://api.whatsapp.com/...)."
)
_MENSAGEM_ENDERECO = "Informe um endereço válido que comece com https://."


def _converter_tipo(tipo: TipoDeContato | str | None) -> TipoDeContato:
    try:
        return TipoDeContato(tipo)
    except ValueError:
        raise ValueError("Tipo de contato inválido.") from None


def _somente_digitos(valor: str | None) -> str:
    if valor is None:
        return ""
    return _SEPARADORES_DE_TELEFONE.sub("", valor)


def _texto_ou_none(valor: str | None) -> str | None:
    if valor is None:
        return None
    return valor.strip() or None


def _dividir_url(endereco: str) -> SplitResult | None:
    """Split an address, or None when it has spaces or is malformed."""
    if not endereco or any(caractere.isspace() for caractere in endereco):
        return None
    if len(endereco) > MAXIMO_CARACTERES_ENDERECO:
        return None
    try:
        partes = urlsplit(endereco)
        partes.port  # noqa: B018 - raises ValueError for an invalid port
    except ValueError:
        return None
    return partes


@dataclass(frozen=True)
class Contato:
    """One contact; `criar` cleans phone masks before validating.

    - WhatsApp with `codigo_pais` is a number; without it, it is a chat link.
    - Telefone always has `codigo_pais` and a digits-only `valor`.
    - E-mail, site and link have no `codigo_pais`; only link has a `rotulo`.
    """

    tipo: TipoDeContato
    valor: str
    codigo_pais: str | None = None
    rotulo: str | None = None

    def __post_init__(self) -> None:
        self._definir("tipo", _converter_tipo(self.tipo))
        self._definir("valor", (self.valor or "").strip())
        if self.codigo_pais is not None:
            self._definir("codigo_pais", self.codigo_pais.strip())
        self._definir("rotulo", _texto_ou_none(self.rotulo))

        self._validar_codigo_do_pais_permitido()
        self._validar_rotulo()
        if self.tipo is TipoDeContato.TELEFONE or self._eh_whatsapp_numero():
            self._validar_numero()
        elif self.tipo is TipoDeContato.WHATSAPP:
            self._validar_link_do_whatsapp()
        elif self.tipo is TipoDeContato.EMAIL:
            self._validar_email()
        else:
            self._validar_endereco_https()

    @classmethod
    def criar(
        cls,
        tipo: TipoDeContato | str | None,
        valor: str | None,
        codigo_pais: str | None = None,
        rotulo: str | None = None,
    ) -> "Contato":
        """Build a contact from raw input, ignoring phone masks."""
        tipo = _converter_tipo(tipo)
        if tipo is TipoDeContato.TELEFONE or (
            tipo is TipoDeContato.WHATSAPP and codigo_pais is not None
        ):
            codigo_pais = _somente_digitos(codigo_pais)
            valor = _somente_digitos(valor)
        return cls(tipo, valor, codigo_pais, rotulo)

    def link_de_conversa(self) -> str:
        """Link that opens a chat; only WhatsApp contacts have one."""
        if self.tipo is not TipoDeContato.WHATSAPP:
            raise ValueError("Só contatos de WhatsApp têm link de conversa.")
        if self.codigo_pais is None:
            return self.valor
        return f"{_URL_BASE_CONVERSA}{self.codigo_pais}{self.valor}"

    def _eh_whatsapp_numero(self) -> bool:
        return (
            self.tipo is TipoDeContato.WHATSAPP
            and self.codigo_pais is not None
        )

    def _validar_codigo_do_pais_permitido(self) -> None:
        if (
            self.tipo not in _TIPOS_COM_CODIGO_DO_PAIS
            and self.codigo_pais is not None
        ):
            raise ValueError(
                "O código do país só vale para número de WhatsApp e telefone."
            )

    def _validar_rotulo(self) -> None:
        if self.rotulo is None:
            return
        if self.tipo is not TipoDeContato.LINK:
            raise ValueError("O rótulo só pode ser usado em links.")
        if len(self.rotulo) > MAXIMO_CARACTERES_ROTULO:
            raise ValueError(
                f"O rótulo deve ter no máximo {MAXIMO_CARACTERES_ROTULO} "
                "caracteres."
            )

    def _validar_numero(self) -> None:
        codigo_pais = self.codigo_pais or ""
        if not codigo_pais:
            raise ValueError("O código do país é obrigatório.")
        if (
            _SO_DIGITOS.fullmatch(codigo_pais) is None
            or len(codigo_pais) > MAXIMO_DIGITOS_CODIGO_PAIS
        ):
            raise ValueError(
                "O código do país deve ter de 1 a "
                f"{MAXIMO_DIGITOS_CODIGO_PAIS} dígitos."
            )
        if not self.valor:
            raise ValueError("Informe o número.")
        if _SO_DIGITOS.fullmatch(self.valor) is None:
            raise ValueError("O número deve ter só dígitos.")
        total = len(codigo_pais) + len(self.valor)
        if not MINIMO_DIGITOS_TELEFONE <= total <= MAXIMO_DIGITOS_TELEFONE:
            raise ValueError(
                "O número (com o código do país) deve ter de "
                f"{MINIMO_DIGITOS_TELEFONE} a {MAXIMO_DIGITOS_TELEFONE} "
                "dígitos."
            )

    def _validar_link_do_whatsapp(self) -> None:
        partes = _dividir_url(self.valor)
        # netloc (not hostname) also rejects user info and ports, such as
        # https://wa.me@evil.com/ or https://wa.me:8080/.
        if (
            partes is None
            or partes.scheme.lower() != _ESQUEMA_HTTPS
            or partes.netloc.lower() not in HOSTS_LINK_WHATSAPP
            or len(partes.path) <= 1
        ):
            raise ValueError(_MENSAGEM_LINK_DO_WHATSAPP)

    def _validar_email(self) -> None:
        self._definir("valor", self.valor.lower())
        if _EMAIL_PATTERN.fullmatch(self.valor) is None:
            raise ValueError("E-mail de contato inválido.")

    def _validar_endereco_https(self) -> None:
        partes = _dividir_url(self.valor)
        if (
            partes is None
            or partes.scheme.lower() != _ESQUEMA_HTTPS
            or "@" in partes.netloc
            or "." not in (partes.hostname or "")
        ):
            raise ValueError(_MENSAGEM_ENDERECO)

    def _definir(self, campo: str, valor: object) -> None:
        object.__setattr__(self, campo, valor)
