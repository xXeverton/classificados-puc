"""HTTP controller for the advertisements feed."""

from flask import g, request
from flask_openapi3 import OpenAPI

from server.api.autenticacao import SEGURANCA_BEARER, exige_sessao
from server.api.presenters.ad_presenter import (
    AdsFeedViewSchema,
    apresenta_feed,
)
from server.api.presenters.error_presenter import (
    ErrorSchema,
    apresenta_erro,
)
from server.core.usecases.erros import ErroDeCasoDeUso
from server.core.usecases.list_ads import ListAds


def register_ads_controller(app: OpenAPI, obter_usuario_da_sessao) -> None:
    """Register the advertisements feed endpoint."""
    protegida = exige_sessao(obter_usuario_da_sessao)

    @app.get(
        "/api/ads",
        security=SEGURANCA_BEARER,
        responses={
            200: AdsFeedViewSchema,
            400: ErrorSchema,
            401: ErrorSchema,
            500: ErrorSchema,
        },
    )
    @protegida
    def ads() -> tuple[dict[str, object], int]:
        page_value = request.args.get("page")
        page = None
        if page_value is not None:
            try:
                page = int(page_value)
            except (TypeError, ValueError):
                return apresenta_erro(
                    "Página deve ser um inteiro positivo."
                ).model_dump(), 400

        search = request.args.get("search")
        ad_type = request.args.get("type")

        repository = app.extensions.get("ad_repository")
        if repository is None:
            return apresenta_erro(
                "Erro interno ao buscar anúncios."
            ).model_dump(), 500

        list_ads = ListAds(repository)
        try:
            result = list_ads.execute(
                usuario=g.usuario,
                page=page,
                search=search,
                ad_type=ad_type,
            )
        except ErroDeCasoDeUso as error:
            return apresenta_erro(str(error)).model_dump(), 401
        except ValueError as error:
            return apresenta_erro(str(error)).model_dump(), 400
        except Exception:
            return apresenta_erro(
                "Erro interno ao buscar anúncios."
            ).model_dump(), 500

        return apresenta_feed(result).model_dump(mode="json"), 200
