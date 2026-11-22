"""Public representation of an advertiser profile and its contacts."""

from pydantic import BaseModel

from server.core.entities.anunciante import Anunciante
from server.core.entities.contato import Contato
from server.core.entities.tipo_de_contato import TipoDeContato


class ContatoViewSchema(BaseModel):
    tipo: str
    codigo_pais: str | None
    valor: str
    rotulo: str | None
    link_de_conversa: str | None


class AnuncianteViewSchema(BaseModel):
    nome_exibicao: str
    contatos: list[ContatoViewSchema]
    foto_url: str | None


def apresenta_contato(contato: Contato) -> ContatoViewSchema:
    eh_whatsapp = contato.tipo is TipoDeContato.WHATSAPP
    return ContatoViewSchema(
        tipo=contato.tipo.value,
        codigo_pais=contato.codigo_pais,
        valor=contato.valor,
        rotulo=contato.rotulo,
        link_de_conversa=contato.link_de_conversa() if eh_whatsapp else None,
    )


def apresenta_anunciante(anunciante: Anunciante) -> AnuncianteViewSchema:
    return AnuncianteViewSchema(
        nome_exibicao=anunciante.nome_exibicao,
        contatos=[apresenta_contato(c) for c in anunciante.contatos],
        foto_url=anunciante.foto_url,
    )
