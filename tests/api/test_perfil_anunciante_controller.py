import io
import json

import pytest

from server.app import create_app
from server.core.entities.politicas_perfil import TAMANHO_MAXIMO_FOTO_BYTES
from tests.api.test_auth_controller import SENHA, Api, bearer
from tests.core.usecases.fakes import (
    EnviadorDeEmailFalso,
    GeradorDeTokenFalso,
    RelogioFalso,
)

JPEG = b"\xff\xd8\xff\xe0" + b"\x00" * 16
PNG = b"\x89PNG\r\n\x1a\n" + b"\x00" * 16
LIMITE_DA_REQUISICAO = 3 * 1024 * 1024

CONTATOS = [
    {"tipo": "whatsapp", "codigo_pais": "55", "valor": "(21) 99999-9999"},
    {"tipo": "email", "valor": "ana@gmail.com"},
    {"tipo": "link", "valor": "https://instagram.com/ana", "rotulo": "Insta"},
]


@pytest.fixture
def api(tmp_path):
    relogio = RelogioFalso()
    enviador = EnviadorDeEmailFalso()
    app = create_app(
        {
            "DATABASE_URL": "sqlite:///:memory:",
            "RELOGIO": relogio,
            "ENVIADOR_EMAIL": enviador,
            "GERADOR_TOKEN": GeradorDeTokenFalso(),
            "CONFIRMACAO_URL_BASE": "http://front.example/confirmar",
            "FOTOS_PERFIL_DIR": str(tmp_path / "fotos"),
        }
    )
    yield Api(app, app.test_client(), relogio, enviador)
    app.extensions["database_engine"].dispose()


@pytest.fixture
def token(api):
    return api.logar()


def formulario(
    nome="Ana Lima", contatos=CONTATOS, foto=None, remover_foto=None
):
    dados = {
        "nome_exibicao": nome,
        "contatos": contatos
        if isinstance(contatos, str)
        else json.dumps(contatos),
    }
    if foto is not None:
        dados["foto"] = (io.BytesIO(foto), "foto.jpg")
    if remover_foto is not None:
        dados["remover_foto"] = remover_foto
    return dados


def salvar(api, token, **kwargs):
    return api.client.put(
        "/perfil-anunciante",
        data=formulario(**kwargs),
        content_type="multipart/form-data",
        headers=bearer(token),
    )


def obter(api, token):
    return api.client.get("/perfil-anunciante", headers=bearer(token))


# --- fluxo principal (CA2, CA3, CA6, CA19) ---


def test_get_404_then_put_200_then_get_200_with_contacts_in_order(
    api, token
):
    antes = obter(api, token)
    assert antes.status_code == 404
    assert antes.json["code"] == "perfil_nao_encontrado"

    salvo = salvar(api, token)
    assert salvo.status_code == 200

    depois = obter(api, token)
    assert depois.status_code == 200
    assert depois.json == salvo.json
    assert depois.json["nome_exibicao"] == "Ana Lima"
    assert depois.json["foto_url"] is None
    assert depois.json["contatos"] == [
        {
            "tipo": "whatsapp",
            "codigo_pais": "55",
            "valor": "21999999999",
            "rotulo": None,
            "link_de_conversa": "https://wa.me/5521999999999",
        },
        {
            "tipo": "email",
            "codigo_pais": None,
            "valor": "ana@gmail.com",
            "rotulo": None,
            "link_de_conversa": None,
        },
        {
            "tipo": "link",
            "codigo_pais": None,
            "valor": "https://instagram.com/ana",
            "rotulo": "Insta",
            "link_de_conversa": None,
        },
    ]


def test_put_again_replaces_the_contacts(api, token):
    salvar(api, token)

    resposta = salvar(
        api,
        token,
        nome="Ana L.",
        contatos=[{"tipo": "email", "valor": "outro@gmail.com"}],
    )

    assert resposta.status_code == 200
    assert resposta.json["nome_exibicao"] == "Ana L."
    assert [c["valor"] for c in obter(api, token).json["contatos"]] == [
        "outro@gmail.com"
    ]


# --- dados inválidos (CA7, CA8, CA12-CA17, CA21, CA22) ---


@pytest.mark.parametrize(
    ("overrides", "trecho"),
    [
        ({"nome": "   "}, "Nome"),
        ({"contatos": []}, "ao menos um"),
        (
            {"contatos": [{"tipo": "email", "valor": "invalido"}]},
            "Contato 1",
        ),
        (
            {"contatos": [{"tipo": "fax", "valor": "123"}]},
            "Tipo de contato inválido",
        ),
        (
            {"contatos": [{"tipo": "email", "valor": "a@b.co"}] * 2},
            "repetidos",
        ),
        (
            {
                "contatos": [
                    {"tipo": "link", "valor": f"https://s{i}.com/x"}
                    for i in range(11)
                ]
            },
            "10",
        ),
    ],
)
def test_invalid_data_answers_400_and_saves_nothing(
    api, token, overrides, trecho
):
    resposta = salvar(api, token, **overrides)

    assert resposta.status_code == 400
    assert resposta.json["code"] == "dados_invalidos"
    assert trecho in resposta.json["message"]
    assert obter(api, token).status_code == 404


@pytest.mark.parametrize(
    "contatos",
    ["nao e json", "{", '{"tipo": "email"}', '"texto"', "[1, 2]", "[null]"],
)
def test_malformed_contacts_json_answers_400(api, token, contatos):
    resposta = salvar(api, token, contatos=contatos)

    assert resposta.status_code == 400
    assert resposta.json["code"] == "dados_invalidos"
    assert obter(api, token).status_code == 404


def test_missing_name_field_answers_400(api, token):
    resposta = api.client.put(
        "/perfil-anunciante",
        data={"contatos": json.dumps(CONTATOS)},
        content_type="multipart/form-data",
        headers=bearer(token),
    )

    assert resposta.status_code == 400


# --- foto (CA23-CA26) ---


def test_put_with_valid_photo_saves_it_and_serves_it(api, token):
    resposta = salvar(api, token, foto=JPEG)

    assert resposta.status_code == 200
    foto_url = resposta.json["foto_url"]
    assert foto_url.startswith("/fotos-perfil/")
    assert foto_url.endswith(".jpg")

    foto = api.client.get(foto_url, headers=bearer(token))
    assert foto.status_code == 200
    assert foto.content_type == "image/jpeg"
    assert foto.data == JPEG


def test_png_is_served_as_png(api, token):
    foto_url = salvar(api, token, foto=PNG).json["foto_url"]

    foto = api.client.get(foto_url, headers=bearer(token))

    assert foto.content_type == "image/png"


def test_put_without_photo_part_saves_without_photo(api, token):
    assert salvar(api, token).json["foto_url"] is None


def test_empty_file_part_means_no_photo(api, token):
    dados = formulario()
    dados["foto"] = (io.BytesIO(b""), "")

    resposta = api.client.put(
        "/perfil-anunciante",
        data=dados,
        content_type="multipart/form-data",
        headers=bearer(token),
    )

    assert resposta.status_code == 200
    assert resposta.json["foto_url"] is None


def test_photo_over_2mb_answers_400(api, token):
    grande = JPEG + b"\x00" * TAMANHO_MAXIMO_FOTO_BYTES

    resposta = salvar(api, token, foto=grande)

    assert resposta.status_code == 400
    assert resposta.json["code"] == "foto_invalida"
    assert obter(api, token).status_code == 404


def test_fake_photo_with_image_name_answers_400(api, token):
    resposta = salvar(api, token, foto=b"nao sou uma imagem")

    assert resposta.status_code == 400
    assert resposta.json["code"] == "foto_invalida"
    assert obter(api, token).status_code == 404


def test_request_over_3mb_answers_413(api, token):
    enorme = JPEG + b"\x00" * LIMITE_DA_REQUISICAO

    resposta = salvar(api, token, foto=enorme)

    assert resposta.status_code == 413
    assert resposta.json["code"] == "arquivo_grande"
    assert obter(api, token).status_code == 404


def test_invalid_photo_keeps_the_previous_profile(api, token):
    anterior = salvar(api, token, foto=JPEG).json

    resposta = salvar(api, token, nome="Outro", foto=b"GIF89a")

    assert resposta.status_code == 400
    assert obter(api, token).json == anterior


def test_keeps_the_photo_when_none_is_sent(api, token):
    foto_url = salvar(api, token, foto=JPEG).json["foto_url"]

    resposta = salvar(api, token, nome="Ana L.")

    assert resposta.json["foto_url"] == foto_url
    assert api.client.get(foto_url, headers=bearer(token)).data == JPEG


@pytest.mark.parametrize("valor", ["true", "1", "on"])
def test_remove_photo_flag_removes_the_photo(api, token, valor):
    foto_url = salvar(api, token, foto=JPEG).json["foto_url"]

    resposta = salvar(api, token, remover_foto=valor)

    assert resposta.json["foto_url"] is None
    gone = api.client.get(foto_url, headers=bearer(token))
    assert gone.status_code == 404


def test_remove_photo_false_keeps_the_photo(api, token):
    foto_url = salvar(api, token, foto=JPEG).json["foto_url"]

    resposta = salvar(api, token, remover_foto="false")

    assert resposta.json["foto_url"] == foto_url


def test_replacing_the_photo_makes_the_old_url_404(api, token):
    antiga = salvar(api, token, foto=JPEG).json["foto_url"]

    nova = salvar(api, token, foto=PNG).json["foto_url"]

    assert nova != antiga
    assert api.client.get(antiga, headers=bearer(token)).status_code == 404
    assert api.client.get(nova, headers=bearer(token)).status_code == 200


# --- acesso às fotos (CA30) ---


def test_photo_without_session_answers_401(api, token):
    foto_url = salvar(api, token, foto=JPEG).json["foto_url"]

    assert api.client.get(foto_url).status_code == 401
    ruim = api.client.get(foto_url, headers=bearer("token-invalido"))
    assert ruim.status_code == 401


def test_missing_photo_answers_404(api, token):
    resposta = api.client.get(
        "/fotos-perfil/naoexiste.jpg", headers=bearer(token)
    )

    assert resposta.status_code == 404


@pytest.mark.parametrize(
    "nome",
    ["..%2F..%2Fsegredo.jpg", "%2e%2e%2fsegredo.jpg", "segredo.txt", "x"],
)
def test_unsafe_photo_names_answer_404(api, token, nome):
    resposta = api.client.get(
        f"/fotos-perfil/{nome}", headers=bearer(token)
    )

    assert resposta.status_code == 404


# --- acesso (CA30) e dono (CA31) ---


def test_all_routes_require_a_session(api):
    gets = ["/perfil-anunciante", "/fotos-perfil/qualquer.jpg"]
    for rota in gets:
        assert api.client.get(rota).status_code == 401
    put = api.client.put(
        "/perfil-anunciante",
        data=formulario(),
        content_type="multipart/form-data",
    )
    assert put.status_code == 401


def test_put_with_invalid_token_answers_401(api):
    resposta = api.client.put(
        "/perfil-anunciante",
        data=formulario(),
        content_type="multipart/form-data",
        headers=bearer("token-invalido"),
    )

    assert resposta.status_code == 401


def test_saved_profile_is_the_one_of_the_session_user(api, token):
    api.cadastrar(
        email="beto@aluno.puc-rio.br", nome_usuario="beto", matricula="2310002"
    )
    api.confirmar()
    token_beto = api.login("beto", SENHA).json["token"]

    salvar(api, token, nome="Ana Lima")
    assert obter(api, token_beto).status_code == 404

    salvar(
        api,
        token_beto,
        nome="Beto",
        contatos=[{"tipo": "email", "valor": "beto@gmail.com"}],
    )

    assert obter(api, token).json["nome_exibicao"] == "Ana Lima"
    assert obter(api, token_beto).json["nome_exibicao"] == "Beto"


def test_the_route_ignores_a_user_id_sent_in_the_request(api, token):
    api.cadastrar(
        email="beto@aluno.puc-rio.br", nome_usuario="beto", matricula="2310002"
    )
    api.confirmar()
    token_beto = api.login("beto", SENHA).json["token"]
    dados = formulario(nome="Invasor")
    dados.update({"usuario_id": "1", "id": "1"})

    resposta = api.client.put(
        "/perfil-anunciante?usuario_id=1",
        data=dados,
        content_type="multipart/form-data",
        headers=bearer(token_beto),
    )

    assert resposta.status_code == 200
    assert obter(api, token).status_code == 404
    assert obter(api, token_beto).json["nome_exibicao"] == "Invasor"
