from dataclasses import replace

import pytest

from server.core.entities.politicas_perfil import TAMANHO_MAXIMO_FOTO_BYTES
from server.core.usecases.erros import (
    DadosInvalidos,
    FotoInvalida,
    PerfilNaoEncontrado,
)
from server.core.usecases.obter_perfil_anunciante import (
    ObterPerfilAnunciante,
)
from server.core.usecases.salvar_perfil_anunciante import (
    DadosDeContato,
    SalvarPerfilAnunciante,
)
from tests.core.usecases.fakes import (
    AnuncianteRepositoryEmMemoria,
    ArmazenamentoDeFotoEmMemoria,
)

JPEG = b"\xff\xd8\xff\xe0" + b"\x00" * 16
PNG = b"\x89PNG\r\n\x1a\n" + b"\x00" * 16
USUARIO_ID = 7


def whatsapp(numero="21999999999"):
    return DadosDeContato("whatsapp", numero, "55", None)


def email(valor="ana@gmail.com"):
    return DadosDeContato("email", valor, None, None)


def link(valor="https://instagram.com/ana", rotulo="Instagram"):
    return DadosDeContato("link", valor, None, rotulo)


class RepositorioQueFalha(AnuncianteRepositoryEmMemoria):

    def salvar(self, anunciante):
        raise RuntimeError("falha ao gravar")


class RepositorioQueFalhaComPerfil(RepositorioQueFalha):

    def __init__(self, existente):
        super().__init__()
        self.anunciantes[1] = replace(existente, id=1)


class Ambiente:

    def __init__(self, anunciantes=None):
        self.anunciantes = anunciantes or AnuncianteRepositoryEmMemoria()
        self.fotos = ArmazenamentoDeFotoEmMemoria()
        self.salvar = SalvarPerfilAnunciante(self.anunciantes, self.fotos)
        self.obter = ObterPerfilAnunciante(self.anunciantes)

    def salvar_perfil(self, **overrides):
        dados = {
            "usuario_id": USUARIO_ID,
            "nome_exibicao": "Ana Lima",
            "contatos": [whatsapp()],
            "foto": None,
            "remover_foto": False,
        }
        dados.update(overrides)
        return self.salvar.executar(**dados)


@pytest.fixture
def ambiente():
    return Ambiente()


# --- ObterPerfilAnunciante (CA2, CA3, CA27) ---


def test_get_returns_the_saved_profile(ambiente):
    ambiente.salvar_perfil()

    perfil = ambiente.obter.executar(USUARIO_ID)

    assert perfil.nome_exibicao == "Ana Lima"


def test_get_without_profile_raises_not_found(ambiente):
    with pytest.raises(PerfilNaoEncontrado):
        ambiente.obter.executar(USUARIO_ID)


def test_get_does_not_return_another_users_profile(ambiente):
    ambiente.salvar_perfil()

    with pytest.raises(PerfilNaoEncontrado):
        ambiente.obter.executar(USUARIO_ID + 1)


# --- SalvarPerfilAnunciante: criar e atualizar (CA6, CA9) ---


def test_creates_the_profile(ambiente):
    perfil = ambiente.salvar_perfil()

    assert perfil.id is not None
    assert perfil.usuario_id == USUARIO_ID
    assert perfil.nome_exibicao == "Ana Lima"
    assert [c.valor for c in perfil.contatos] == ["21999999999"]
    assert ambiente.anunciantes.buscar_por_usuario_id(USUARIO_ID) == perfil


def test_update_replaces_data_and_contacts(ambiente):
    ambiente.salvar_perfil()

    perfil = ambiente.salvar_perfil(
        nome_exibicao="Ana L.", contatos=[email(), link()]
    )

    assert perfil.nome_exibicao == "Ana L."
    assert [c.tipo.value for c in perfil.contatos] == ["email", "link"]
    assert len(ambiente.anunciantes.anunciantes) == 1


# --- dados inválidos (CA7, CA8, CA12-CA17, CA21, CA22) ---


@pytest.mark.parametrize("nome", ["", "   "])
def test_name_is_required(ambiente, nome):
    with pytest.raises(DadosInvalidos, match="Nome"):
        ambiente.salvar_perfil(nome_exibicao=nome)

    assert ambiente.anunciantes.anunciantes == {}


def test_at_least_one_contact_is_required(ambiente):
    with pytest.raises(DadosInvalidos, match="ao menos um"):
        ambiente.salvar_perfil(contatos=[])

    assert ambiente.anunciantes.anunciantes == {}


@pytest.mark.parametrize(
    "contato",
    [
        DadosDeContato("fax", "123", None, None),
        DadosDeContato("whatsapp", "abc", "55", None),
        DadosDeContato("whatsapp", "999", "55", None),
        DadosDeContato("whatsapp", "https://exemplo.com/x", None, None),
        DadosDeContato("telefone", "21999999999", None, None),
        DadosDeContato("email", "sem-arroba", None, None),
        DadosDeContato("site", "http://exemplo.com", None, None),
        DadosDeContato("link", "javascript:alert(1)", None, None),
    ],
)
def test_invalid_contact_is_refused_and_nothing_is_saved(ambiente, contato):
    with pytest.raises(DadosInvalidos):
        ambiente.salvar_perfil(contatos=[contato])

    assert ambiente.anunciantes.anunciantes == {}


def test_error_says_which_contact_failed(ambiente):
    with pytest.raises(DadosInvalidos) as erro:
        ambiente.salvar_perfil(
            contatos=[whatsapp(), email("invalido"), link()]
        )

    assert erro.value.mensagem.startswith("Contato 2:")


def test_more_than_ten_contacts_is_refused(ambiente):
    contatos = [link(f"https://site{i}.com/x") for i in range(11)]

    with pytest.raises(DadosInvalidos, match="10"):
        ambiente.salvar_perfil(contatos=contatos)

    assert ambiente.anunciantes.anunciantes == {}


def test_ten_contacts_are_accepted(ambiente):
    contatos = [link(f"https://site{i}.com/x") for i in range(10)]

    assert len(ambiente.salvar_perfil(contatos=contatos).contatos) == 10


def test_repeated_contacts_are_refused(ambiente):
    with pytest.raises(DadosInvalidos, match="repetidos"):
        ambiente.salvar_perfil(contatos=[email(), email("ANA@gmail.com")])

    assert ambiente.anunciantes.anunciantes == {}


# --- ordem e remoção (CA19, CA20) ---


def test_contact_order_is_preserved(ambiente):
    perfil = ambiente.salvar_perfil(
        contatos=[link(), email(), whatsapp(), link("https://b.com/x")]
    )

    assert [c.tipo.value for c in perfil.contatos] == [
        "link", "email", "whatsapp", "link",
    ]
    lido = ambiente.obter.executar(USUARIO_ID)
    assert lido.contatos == perfil.contatos


def test_removed_contact_is_gone_after_saving(ambiente):
    ambiente.salvar_perfil(contatos=[whatsapp(), email()])

    perfil = ambiente.salvar_perfil(contatos=[email()])

    assert [c.tipo.value for c in perfil.contatos] == ["email"]


def test_removing_every_contact_is_refused_and_keeps_the_old_list(ambiente):
    ambiente.salvar_perfil(contatos=[whatsapp(), email()])

    with pytest.raises(DadosInvalidos):
        ambiente.salvar_perfil(contatos=[])

    assert len(ambiente.obter.executar(USUARIO_ID).contatos) == 2


# --- foto (CA23-CA26, RN8) ---


def test_saves_without_photo(ambiente):
    perfil = ambiente.salvar_perfil()

    assert perfil.foto_url is None
    assert ambiente.fotos.fotos == {}


def test_saves_with_valid_photo(ambiente):
    perfil = ambiente.salvar_perfil(foto=JPEG)

    assert perfil.foto_url is not None
    assert perfil.foto_url.endswith(".jpg")
    assert ambiente.fotos.ler(perfil.foto_url) == JPEG


@pytest.mark.parametrize(
    "foto",
    [
        pytest.param(b"GIF89a" + b"\x00" * 16, id="gif"),
        pytest.param(b"texto com nome .jpg", id="texto"),
        pytest.param(b"", id="vazio"),
        pytest.param(
            JPEG + b"\x00" * TAMANHO_MAXIMO_FOTO_BYTES, id="grande"
        ),
    ],
)
def test_invalid_photo_saves_nothing(ambiente, foto):
    with pytest.raises(FotoInvalida):
        ambiente.salvar_perfil(foto=foto)

    assert ambiente.anunciantes.anunciantes == {}
    assert ambiente.fotos.fotos == {}


def test_invalid_photo_keeps_previous_data(ambiente):
    original = ambiente.salvar_perfil(foto=JPEG)

    with pytest.raises(FotoInvalida):
        ambiente.salvar_perfil(nome_exibicao="Outro", foto=b"GIF89a")

    assert ambiente.obter.executar(USUARIO_ID) == original
    assert list(ambiente.fotos.fotos) == [original.foto_url]


def test_invalid_contact_does_not_store_photo_nor_profile(ambiente):
    with pytest.raises(DadosInvalidos):
        ambiente.salvar_perfil(foto=JPEG, contatos=[email("invalido")])

    assert ambiente.anunciantes.anunciantes == {}
    assert ambiente.fotos.fotos == {}


def test_invalid_name_does_not_store_photo(ambiente):
    with pytest.raises(DadosInvalidos):
        ambiente.salvar_perfil(foto=JPEG, nome_exibicao=" ")

    assert ambiente.fotos.fotos == {}


def test_keeps_current_photo_when_none_is_sent(ambiente):
    original = ambiente.salvar_perfil(foto=JPEG)

    perfil = ambiente.salvar_perfil(nome_exibicao="Ana L.")

    assert perfil.foto_url == original.foto_url
    assert ambiente.fotos.ler(original.foto_url) == JPEG


def test_remove_photo_clears_url_and_deletes_the_file(ambiente):
    original = ambiente.salvar_perfil(foto=JPEG)

    perfil = ambiente.salvar_perfil(remover_foto=True)

    assert perfil.foto_url is None
    assert ambiente.fotos.ler(original.foto_url) is None
    assert ambiente.obter.executar(USUARIO_ID).foto_url is None


def test_replacing_the_photo_deletes_the_old_one(ambiente):
    original = ambiente.salvar_perfil(foto=JPEG)

    perfil = ambiente.salvar_perfil(foto=PNG)

    assert perfil.foto_url != original.foto_url
    assert perfil.foto_url.endswith(".png")
    assert ambiente.fotos.ler(original.foto_url) is None
    assert ambiente.fotos.ler(perfil.foto_url) == PNG


def test_new_photo_wins_over_remove_flag(ambiente):
    perfil = ambiente.salvar_perfil(foto=JPEG, remover_foto=True)

    assert perfil.foto_url is not None


def test_removing_photo_of_profile_without_photo_is_harmless(ambiente):
    perfil = ambiente.salvar_perfil(remover_foto=True)

    assert perfil.foto_url is None


def test_repository_failure_deletes_the_new_photo():
    ambiente = Ambiente(RepositorioQueFalha())

    with pytest.raises(RuntimeError):
        ambiente.salvar_perfil(foto=JPEG)

    assert ambiente.fotos.fotos == {}


def test_repository_failure_keeps_the_old_photo(ambiente):
    original = ambiente.salvar_perfil(foto=JPEG)
    ambiente.salvar = SalvarPerfilAnunciante(
        RepositorioQueFalhaComPerfil(original), ambiente.fotos
    )

    with pytest.raises(RuntimeError):
        ambiente.salvar_perfil(foto=PNG)

    assert list(ambiente.fotos.fotos) == [original.foto_url]
