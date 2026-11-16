from app.main import create_app
from infra.repositories.autenticador_mock import AutenticadorMock
from use_cases.identidade_autenticada import UsuarioAutenticado


def autenticador_com_usuario_mock():
    return AutenticadorMock(
        UsuarioAutenticado(
            id_usuario=1,
            nome_exibicao="Anunciante de teste",
        )
    )


def test_new_ad_page_requires_authenticated_user():
    client = create_app().test_client()

    response = client.get("/anuncios/novo")

    assert response.status_code == 302
    assert response.headers["Location"] == "/login?next=/anuncios/novo"


def test_new_ad_page_renders_visual_preview_for_injected_mock_user():
    client = create_app(
        autenticador=autenticador_com_usuario_mock()
    ).test_client()

    response = client.get("/anuncios/novo")

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "Prévia da tela" in html
    assert "Novo anúncio" in html
    assert 'id="titulo"' in html
    assert 'id="categoria"' in html
    assert 'id="estado_conservacao"' in html
    assert 'id="descricao"' in html
    assert 'id="preco"' in html
    assert 'type="button" disabled' in html


def test_login_destination_explains_that_mock_does_not_authenticate():
    response = create_app().test_client().get("/login")

    assert response.status_code == 503
    assert "O mock temporário não realiza login." in (
        response.get_data(as_text=True)
    )


def test_home_redirects_to_new_ad_preview():
    response = create_app().test_client().get("/")

    assert response.status_code == 302
    assert response.headers["Location"] == "/anuncios/novo"
