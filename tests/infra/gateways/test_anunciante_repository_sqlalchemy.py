import pytest
from sqlalchemy import text

from server.core.entities.anunciante import Anunciante
from server.core.entities.contato import Contato
from server.core.entities.usuario import Usuario
from server.infra.db.database import create_session_factory
from server.infra.gateways.anunciante_repository_sqlalchemy import (
    AnuncianteRepositorySQLAlchemy,
)
from server.infra.gateways.usuario_repository_sqlalchemy import (
    UsuarioRepositorySQLAlchemy,
)

EMAIL = Contato.criar("email", "ana@gmail.com")
WHATSAPP_NUMERO = Contato.criar(
    "whatsapp", "(21) 99999-8888", codigo_pais="+55"
)
WHATSAPP_LINK = Contato.criar("whatsapp", "https://wa.me/message/ABCDEF123456")
TELEFONE = Contato.criar("telefone", "21 3333-4444", codigo_pais="55")
SITE = Contato.criar("site", "https://loja.com.br")
LINK_COM_ROTULO = Contato.criar(
    "link", "https://instagram.com/ana", rotulo="Instagram"
)
LINK_SEM_ROTULO = Contato.criar("link", "https://linktr.ee/ana")


@pytest.fixture
def session_factory(database_engine):
    return create_session_factory(database_engine)


@pytest.fixture
def usuario(session_factory) -> Usuario:
    return UsuarioRepositorySQLAlchemy(session_factory).salvar(
        Usuario(
            nome="Ana",
            email="ana@aluno.puc-rio.br",
            nome_usuario="ana",
            vinculo="aluno",
            senha_hash="hash",
        )
    )


@pytest.fixture
def anunciantes(session_factory):
    return AnuncianteRepositorySQLAlchemy(session_factory)


def novo_anunciante(usuario, **overrides) -> Anunciante:
    dados = {
        "usuario_id": usuario.id,
        "nome_exibicao": "Ana Vendas",
        "contatos": [EMAIL, WHATSAPP_NUMERO],
    }
    dados.update(overrides)
    return Anunciante(**dados)


def contar(database_engine, tabela: str) -> int:
    with database_engine.connect() as connection:
        return connection.execute(
            text(f"SELECT count(*) FROM {tabela}")
        ).scalar_one()


def test_buscar_por_usuario_id_returns_none_without_profile(
    anunciantes, usuario
):
    assert anunciantes.buscar_por_usuario_id(usuario.id) is None


def test_salvar_creates_profile_with_internal_id(anunciantes, usuario):
    salvo = anunciantes.salvar(novo_anunciante(usuario))

    assert salvo.id is not None
    assert salvo == novo_anunciante(usuario, id=salvo.id)
    assert anunciantes.buscar_por_usuario_id(usuario.id) == salvo


def test_salvar_round_trips_every_kind_of_contact_in_order(
    anunciantes, usuario
):
    contatos = [
        LINK_COM_ROTULO,
        TELEFONE,
        WHATSAPP_LINK,
        EMAIL,
        SITE,
        WHATSAPP_NUMERO,
        LINK_SEM_ROTULO,
    ]

    anunciantes.salvar(novo_anunciante(usuario, contatos=contatos))

    lido = anunciantes.buscar_por_usuario_id(usuario.id)
    assert lido.contatos == tuple(contatos)


def test_salvar_round_trips_both_whatsapp_forms(anunciantes, usuario):
    anunciantes.salvar(
        novo_anunciante(usuario, contatos=[WHATSAPP_NUMERO, WHATSAPP_LINK])
    )

    numero, link = anunciantes.buscar_por_usuario_id(usuario.id).contatos
    assert (numero.codigo_pais, numero.valor) == ("55", "21999998888")
    assert numero.link_de_conversa() == "https://wa.me/5521999998888"
    assert link.codigo_pais is None
    assert link.link_de_conversa() == "https://wa.me/message/ABCDEF123456"


def test_salvar_round_trips_photo_and_keeps_labels(anunciantes, usuario):
    anunciantes.salvar(
        novo_anunciante(
            usuario,
            contatos=[LINK_COM_ROTULO, LINK_SEM_ROTULO],
            foto_url="/fotos-perfil/abc.jpg",
        )
    )

    lido = anunciantes.buscar_por_usuario_id(usuario.id)
    assert lido.foto_url == "/fotos-perfil/abc.jpg"
    assert [c.rotulo for c in lido.contatos] == ["Instagram", None]


def test_salvar_updates_profile_and_replaces_the_whole_contact_list(
    database_engine, anunciantes, usuario
):
    criado = anunciantes.salvar(
        novo_anunciante(
            usuario,
            contatos=[EMAIL, WHATSAPP_NUMERO, SITE],
            foto_url="/fotos-perfil/abc.jpg",
        )
    )

    atualizado = anunciantes.salvar(
        novo_anunciante(
            usuario,
            nome_exibicao="Ana Ateliê",
            contatos=[LINK_COM_ROTULO, EMAIL],
        )
    )

    assert atualizado.id == criado.id
    lido = anunciantes.buscar_por_usuario_id(usuario.id)
    assert lido == atualizado
    assert lido.nome_exibicao == "Ana Ateliê"
    assert lido.contatos == (LINK_COM_ROTULO, EMAIL)
    assert lido.foto_url is None
    assert contar(database_engine, "anunciantes") == 1
    assert contar(database_engine, "contatos_anunciante") == 2


def test_salvar_can_reorder_contacts(anunciantes, usuario):
    anunciantes.salvar(novo_anunciante(usuario, contatos=[EMAIL, SITE]))

    anunciantes.salvar(novo_anunciante(usuario, contatos=[SITE, EMAIL]))

    assert anunciantes.buscar_por_usuario_id(usuario.id).contatos == (
        SITE,
        EMAIL,
    )


def test_salvar_does_not_touch_other_users_profiles(
    session_factory, anunciantes, usuario
):
    outro = UsuarioRepositorySQLAlchemy(session_factory).salvar(
        Usuario(
            nome="Bia",
            email="bia@aluno.puc-rio.br",
            nome_usuario="bia",
            vinculo="funcionario",
            senha_hash="hash",
        )
    )
    anunciantes.salvar(novo_anunciante(usuario))

    anunciantes.salvar(
        novo_anunciante(outro, nome_exibicao="Bia Doces", contatos=[SITE])
    )
    anunciantes.salvar(novo_anunciante(outro, contatos=[LINK_SEM_ROTULO]))

    ana = anunciantes.buscar_por_usuario_id(usuario.id)
    bia = anunciantes.buscar_por_usuario_id(outro.id)
    assert ana.nome_exibicao == "Ana Vendas"
    assert ana.contatos == (EMAIL, WHATSAPP_NUMERO)
    assert bia.contatos == (LINK_SEM_ROTULO,)


def test_salvar_is_all_or_nothing_when_a_contact_cannot_be_stored(
    database_engine, anunciantes, usuario
):
    anunciantes.salvar(novo_anunciante(usuario))
    # Same kind and value under two positions is fine for the database, but
    # an invalid row (bypassing the entity) must roll back the whole save.
    with database_engine.begin() as connection:
        connection.execute(
            text(
                "CREATE TRIGGER falha_ao_inserir BEFORE INSERT ON "
                "contatos_anunciante WHEN NEW.valor = 'quebra@gmail.com' "
                "BEGIN SELECT RAISE(ABORT, 'falha simulada'); END"
            )
        )

    with pytest.raises(Exception, match="falha simulada"):
        anunciantes.salvar(
            novo_anunciante(
                usuario,
                nome_exibicao="Novo nome",
                contatos=[Contato.criar("email", "quebra@gmail.com")],
            )
        )

    lido = anunciantes.buscar_por_usuario_id(usuario.id)
    assert lido.nome_exibicao == "Ana Vendas"
    assert lido.contatos == (EMAIL, WHATSAPP_NUMERO)


def test_removing_user_removes_its_profile_and_contacts(
    database_engine, session_factory, anunciantes, usuario
):
    anunciantes.salvar(novo_anunciante(usuario))

    UsuarioRepositorySQLAlchemy(session_factory).remover(usuario.id)

    assert anunciantes.buscar_por_usuario_id(usuario.id) is None
    assert contar(database_engine, "contatos_anunciante") == 0
