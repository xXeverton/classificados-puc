import pytest

from server.core.entities.anunciante import Anunciante
from server.core.entities.contato import Contato
from server.core.entities.tipo_de_contato import TipoDeContato

EMAIL = Contato.criar("email", "ana@gmail.com")
WHATSAPP = Contato.criar("whatsapp", "21999998888", codigo_pais="55")
LINK = Contato.criar("link", "https://instagram.com/ana", rotulo="Instagram")


def criar_anunciante(**overrides) -> Anunciante:
    dados = {
        "usuario_id": 1,
        "nome_exibicao": "Ana Vendas",
        "contatos": [EMAIL, WHATSAPP],
    }
    dados.update(overrides)
    return Anunciante(**dados)


def contatos_distintos(quantidade: int) -> list[Contato]:
    return [
        Contato.criar("link", f"https://loja{i}.com.br")
        for i in range(quantidade)
    ]


def test_anunciante_keeps_valid_data():
    anunciante = criar_anunciante()

    assert anunciante.usuario_id == 1
    assert anunciante.nome_exibicao == "Ana Vendas"
    assert anunciante.contatos == (EMAIL, WHATSAPP)
    assert anunciante.foto_url is None
    assert anunciante.id is None


@pytest.mark.parametrize("nome", ["", "   "])
def test_anunciante_requires_display_name(nome):
    with pytest.raises(ValueError, match="Nome de exibição"):
        criar_anunciante(nome_exibicao=nome)


def test_anunciante_strips_display_name():
    assert criar_anunciante(nome_exibicao="  Ana  ").nome_exibicao == "Ana"


def test_anunciante_stores_contacts_as_a_tuple_in_the_given_order():
    anunciante = criar_anunciante(contatos=[LINK, EMAIL, WHATSAPP])

    assert anunciante.contatos == (LINK, EMAIL, WHATSAPP)
    assert isinstance(anunciante.contatos, tuple)


@pytest.mark.parametrize("contato", [EMAIL, WHATSAPP, LINK])
def test_anunciante_accepts_a_single_contact_of_any_kind(contato):
    assert criar_anunciante(contatos=[contato]).contatos == (contato,)


@pytest.mark.parametrize("contatos", [[], ()])
def test_anunciante_requires_at_least_one_contact(contatos):
    with pytest.raises(ValueError, match="ao menos um contato"):
        criar_anunciante(contatos=contatos)


def test_anunciante_accepts_exactly_ten_contacts():
    anunciante = criar_anunciante(contatos=contatos_distintos(10))

    assert len(anunciante.contatos) == 10


def test_anunciante_rejects_more_than_ten_contacts():
    with pytest.raises(ValueError, match="no máximo 10 contatos"):
        criar_anunciante(contatos=contatos_distintos(11))


def test_anunciante_rejects_repeated_contacts():
    with pytest.raises(ValueError, match="repetido"):
        criar_anunciante(contatos=[EMAIL, WHATSAPP, EMAIL])


def test_repeated_contact_ignores_only_the_label():
    primeiro = Contato.criar("link", "https://x.com/a", rotulo="Um")
    segundo = Contato.criar("link", "https://x.com/a", rotulo="Dois")

    with pytest.raises(ValueError, match="repetido"):
        criar_anunciante(contatos=[primeiro, segundo])


def test_same_value_in_different_kinds_is_not_a_repeat():
    site = Contato.criar("site", "https://loja.com.br")
    link = Contato.criar("link", "https://loja.com.br")
    telefone = Contato.criar("telefone", "21999998888", codigo_pais="55")
    whatsapp = Contato.criar("whatsapp", "21999998888", codigo_pais="55")

    anunciante = criar_anunciante(contatos=[site, link, telefone, whatsapp])

    assert len(anunciante.contatos) == 4
    assert {c.tipo for c in anunciante.contatos} == {
        TipoDeContato.SITE,
        TipoDeContato.LINK,
        TipoDeContato.TELEFONE,
        TipoDeContato.WHATSAPP,
    }


def test_same_number_with_other_country_code_is_not_a_repeat():
    brasil = Contato.criar("telefone", "21999998888", codigo_pais="55")
    outro = Contato.criar("telefone", "21999998888", codigo_pais="351")

    assert len(criar_anunciante(contatos=[brasil, outro]).contatos) == 2


def test_anunciante_turns_empty_photo_into_none():
    assert criar_anunciante(foto_url=" ").foto_url is None


def test_com_foto_and_sem_foto_return_new_instances():
    anunciante = criar_anunciante()

    com_foto = anunciante.com_foto("/fotos-perfil/abc.jpg")
    sem_foto = com_foto.sem_foto()

    assert anunciante.foto_url is None
    assert com_foto.foto_url == "/fotos-perfil/abc.jpg"
    assert sem_foto.foto_url is None
    assert sem_foto.contatos == anunciante.contatos
