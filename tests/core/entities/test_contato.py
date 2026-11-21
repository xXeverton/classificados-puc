import pytest

from server.core.entities.contato import Contato
from server.core.entities.tipo_de_contato import TipoDeContato

WHATSAPP = TipoDeContato.WHATSAPP
TELEFONE = TipoDeContato.TELEFONE
EMAIL = TipoDeContato.EMAIL
SITE = TipoDeContato.SITE
LINK = TipoDeContato.LINK


# --- tipo -------------------------------------------------------------------


def test_criar_accepts_the_type_as_text_or_as_enum():
    por_texto = Contato.criar("email", "ana@gmail.com")
    por_enum = Contato.criar(EMAIL, "ana@gmail.com")

    assert por_texto == por_enum
    assert por_texto.tipo is EMAIL


@pytest.mark.parametrize("tipo", ["fax", "", "WhatsApp", None])
def test_criar_rejects_unknown_type(tipo):
    with pytest.raises(ValueError, match="Tipo de contato"):
        Contato.criar(tipo, "ana@gmail.com")


# --- WhatsApp por número e telefone (mesma regra de dígitos) ----------------


@pytest.mark.parametrize("tipo", [WHATSAPP, TELEFONE])
@pytest.mark.parametrize(
    ("codigo_pais", "numero", "codigo_esperado", "numero_esperado"),
    [
        ("55", "21999998888", "55", "21999998888"),
        ("+55", "(21) 99999-8888", "55", "21999998888"),
        (" 1 ", "415.555.2671", "1", "4155552671"),
        ("351", "912 345 678", "351", "912345678"),
    ],
)
def test_number_keeps_only_digits(
    tipo, codigo_pais, numero, codigo_esperado, numero_esperado
):
    contato = Contato.criar(tipo, numero, codigo_pais=codigo_pais)

    assert contato.tipo is tipo
    assert contato.codigo_pais == codigo_esperado
    assert contato.valor == numero_esperado


@pytest.mark.parametrize("tipo", [WHATSAPP, TELEFONE])
@pytest.mark.parametrize("codigo_pais", ["", " ", "+"])
def test_number_requires_country_code(tipo, codigo_pais):
    with pytest.raises(ValueError, match="código do país"):
        Contato.criar(tipo, "21999998888", codigo_pais=codigo_pais)


def test_telefone_requires_country_code():
    with pytest.raises(ValueError, match="código do país"):
        Contato.criar(TELEFONE, "21999998888")


@pytest.mark.parametrize("tipo", [WHATSAPP, TELEFONE])
@pytest.mark.parametrize("codigo_pais", ["1234", "5a"])
def test_number_rejects_invalid_country_code(tipo, codigo_pais):
    with pytest.raises(ValueError, match="código do país"):
        Contato.criar(tipo, "99998888", codigo_pais=codigo_pais)


@pytest.mark.parametrize("tipo", [WHATSAPP, TELEFONE])
@pytest.mark.parametrize("numero", [None, "", " ", "()-"])
def test_number_requires_number(tipo, numero):
    with pytest.raises(ValueError, match="número"):
        Contato.criar(tipo, numero, codigo_pais="55")


@pytest.mark.parametrize("tipo", [WHATSAPP, TELEFONE])
@pytest.mark.parametrize(
    ("codigo_pais", "numero"),
    [("1", "2345678"), ("55", "1234567890123")],
    ids=["8_digitos", "15_digitos"],
)
def test_number_accepts_total_length_limits(tipo, codigo_pais, numero):
    assert Contato.criar(tipo, numero, codigo_pais=codigo_pais).valor == numero


@pytest.mark.parametrize("tipo", [WHATSAPP, TELEFONE])
@pytest.mark.parametrize(
    ("codigo_pais", "numero"),
    [("1", "234567"), ("55", "12345678901234")],
    ids=["7_digitos", "16_digitos"],
)
def test_number_rejects_total_length_outside_limits(
    tipo, codigo_pais, numero
):
    with pytest.raises(ValueError, match="8 a 15 dígitos"):
        Contato.criar(tipo, numero, codigo_pais=codigo_pais)


@pytest.mark.parametrize("tipo", [WHATSAPP, TELEFONE])
@pytest.mark.parametrize(
    "numero", ["2199999abcd", "２１９９９９９８８８８"],
    ids=["letras", "digitos_nao_ascii"],
)
def test_number_rejects_non_digits(tipo, numero):
    with pytest.raises(ValueError, match="dígitos"):
        Contato.criar(tipo, numero, codigo_pais="55")


# --- WhatsApp por link ------------------------------------------------------


@pytest.mark.parametrize(
    "link",
    [
        "https://wa.me/5521999998888",
        "https://wa.me/message/ABCDEF123456",
        "https://api.whatsapp.com/send?phone=5521999998888",
        "  https://wa.me/5521999998888  ",
        "HTTPS://WA.ME/5521999998888",
    ],
)
def test_whatsapp_link_accepts_chat_links(link):
    contato = Contato.criar(WHATSAPP, link)

    assert contato.valor == link.strip()
    assert contato.codigo_pais is None


@pytest.mark.parametrize(
    "link",
    [
        "",
        "   ",
        None,
        "wa.me/5521999998888",
        "21999998888",
        "http://wa.me/5521999998888",
        "https://wa.me",
        "https://wa.me/",
        "https://evil.com/wa.me/5521999998888",
        "https://wa.me.evil.com/5521999998888",
        "https://wa.me@evil.com/5521999998888",
        "https://wa.me:8080/5521999998888",
        "https://chat.whatsapp.com/ABCDEF",
        "javascript:alert(1)//wa.me/5521",
        "https://wa.me/5521 999998888",
    ],
)
def test_whatsapp_link_rejects_other_links(link):
    with pytest.raises(ValueError, match="link de conversa"):
        Contato.criar(WHATSAPP, link)


# --- e-mail -----------------------------------------------------------------


@pytest.mark.parametrize(
    "email",
    [
        "ana@gmail.com",
        "ana.silva+loja@outlook.com.br",
        "contato@puc-rio.br",
        "ana@aluno.puc-rio.br",
    ],
)
def test_email_accepts_any_domain(email):
    assert Contato.criar(EMAIL, email).valor == email


@pytest.mark.parametrize(
    "email",
    [
        "",
        " ",
        None,
        "ana",
        "ana@",
        "@gmail.com",
        "ana@gmail",
        "ana @gmail.com",
        "a@b@c.com",
    ],
)
def test_email_rejects_invalid_format(email):
    with pytest.raises(ValueError, match="E-mail"):
        Contato.criar(EMAIL, email)


def test_email_is_stripped_and_lowercased():
    assert Contato.criar(EMAIL, "  Ana@GMail.com ").valor == "ana@gmail.com"


# --- site e link ------------------------------------------------------------


@pytest.mark.parametrize("tipo", [SITE, LINK])
@pytest.mark.parametrize(
    "endereco",
    [
        "https://loja.com.br",
        "https://instagram.com/ana.vendas",
        "https://exemplo.com:8443/caminho?a=1#topo",
        "HTTPS://LOJA.COM",
    ],
)
def test_https_address_is_accepted_as_informed(tipo, endereco):
    assert Contato.criar(tipo, endereco).valor == endereco


@pytest.mark.parametrize("tipo", [SITE, LINK])
def test_https_address_is_stripped(tipo):
    assert Contato.criar(tipo, "  https://loja.com.br ").valor == (
        "https://loja.com.br"
    )


@pytest.mark.parametrize("tipo", [SITE, LINK])
@pytest.mark.parametrize(
    "endereco",
    [
        "",
        " ",
        None,
        "loja.com.br",
        "http://loja.com.br",
        "ftp://loja.com.br",
        "javascript:alert(1)",
        "https://",
        "https:///caminho",
        "https://localhost",
        "https://usuario@evil.com",
        "https://usuario:senha@evil.com",
        "https://loja .com.br",
        "https://loja.com.br/a b",
        "https://[invalido",
        "https://loja.com.br:porta",
        "https://" + "a" * 2050 + ".com",
    ],
)
def test_https_address_rejects_everything_else(tipo, endereco):
    with pytest.raises(ValueError, match="https://"):
        Contato.criar(tipo, endereco)


# --- rótulo -----------------------------------------------------------------


def test_link_accepts_optional_label():
    com_rotulo = Contato.criar(
        LINK, "https://instagram.com/ana", rotulo=" Instagram "
    )
    sem_rotulo = Contato.criar(LINK, "https://instagram.com/ana")

    assert com_rotulo.rotulo == "Instagram"
    assert sem_rotulo.rotulo is None


def test_link_turns_blank_label_into_none():
    assert Contato.criar(LINK, "https://x.com/a", rotulo="  ").rotulo is None


def test_label_length_limit():
    assert Contato.criar(LINK, "https://x.com/a", rotulo="a" * 40)
    with pytest.raises(ValueError, match="40 caracteres"):
        Contato.criar(LINK, "https://x.com/a", rotulo="a" * 41)


@pytest.mark.parametrize(
    ("tipo", "valor", "extra"),
    [
        (SITE, "https://loja.com.br", {}),
        (EMAIL, "ana@gmail.com", {}),
        (TELEFONE, "21999998888", {"codigo_pais": "55"}),
        (WHATSAPP, "21999998888", {"codigo_pais": "55"}),
        (WHATSAPP, "https://wa.me/5521999998888", {}),
    ],
)
def test_label_is_only_for_links(tipo, valor, extra):
    with pytest.raises(ValueError, match="rótulo"):
        Contato.criar(tipo, valor, rotulo="Loja", **extra)


# --- código do país onde não cabe -------------------------------------------


@pytest.mark.parametrize(
    ("tipo", "valor"),
    [
        (EMAIL, "ana@gmail.com"),
        (SITE, "https://loja.com.br"),
        (LINK, "https://instagram.com/ana"),
    ],
)
def test_country_code_is_only_for_whatsapp_number_and_telefone(tipo, valor):
    with pytest.raises(ValueError, match="código do país"):
        Contato.criar(tipo, valor, codigo_pais="55")


# --- construção direta ------------------------------------------------------


def test_direct_construction_validates_without_cleaning_masks():
    with pytest.raises(ValueError):
        Contato(TELEFONE, "(21) 99999-8888", codigo_pais="55")
    with pytest.raises(ValueError):
        Contato(WHATSAPP, "123", codigo_pais="55")


def test_contatos_are_immutable_and_comparable_by_value():
    contato = Contato.criar(EMAIL, "ana@gmail.com")

    assert contato == Contato.criar(EMAIL, "ANA@gmail.com")
    assert len({contato, Contato.criar(EMAIL, "ana@gmail.com")}) == 1
    with pytest.raises(AttributeError):
        contato.valor = "outro@gmail.com"


# --- link de conversa -------------------------------------------------------


def test_link_de_conversa_for_whatsapp_number():
    contato = Contato.criar(WHATSAPP, "(21) 99999-8888", codigo_pais="+55")

    assert contato.link_de_conversa() == "https://wa.me/5521999998888"


def test_link_de_conversa_for_whatsapp_link_is_the_link_itself():
    link = "https://wa.me/message/ABCDEF123456"

    assert Contato.criar(WHATSAPP, link).link_de_conversa() == link


@pytest.mark.parametrize(
    ("tipo", "valor", "extra"),
    [
        (EMAIL, "ana@gmail.com", {}),
        (SITE, "https://loja.com.br", {}),
        (TELEFONE, "21999998888", {"codigo_pais": "55"}),
    ],
)
def test_link_de_conversa_only_exists_for_whatsapp(tipo, valor, extra):
    with pytest.raises(ValueError, match="WhatsApp"):
        Contato.criar(tipo, valor, **extra).link_de_conversa()
