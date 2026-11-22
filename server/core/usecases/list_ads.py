"""Use case for listing advertisements available in the feed."""

from math import ceil

from server.core.entities.usuario import Usuario
from server.core.interfaces.ad_repository_interface import AdRepository
from server.core.usecases.erros import ErroDeCasoDeUso


class ListAds:
    """List published advertisements for an authenticated user."""

    PER_PAGE = 20
    VALID_TYPES = {"all", "product", "service"}

    def __init__(self, repository: AdRepository):
        self.repository = repository

    def execute(
        self,
        usuario: Usuario | None,
        page: int | None = None,
        search: str | None = None,
        ad_type: str | None = None,
    ) -> dict[str, object]:
        if usuario is None:
            raise ErroDeCasoDeUso(
                "Usuário não autenticado.",
            )

        page = self._validate_page(page)
        self._validate_search(search)
        self._validate_ad_type(ad_type)

        # The requested page is kept even with a search or filter, so the
        # user can page through results. Going back to the first page when
        # a search or filter changes (RN11) is the client's job: only it
        # knows whether the filter changed or the user just turned a page.
        items, total_items = self.repository.list_published(
            page=page,
            per_page=self.PER_PAGE,
            search=search,
            ad_type=ad_type,
        )
        total_pages = ceil(total_items / self.PER_PAGE)

        result: dict[str, object] = {
            "items": items,
            "page": page,
            "per_page": self.PER_PAGE,
            "total_pages": total_pages,
            "total_items": total_items,
        }
        if total_items == 0:
            result["message"] = "Nenhum anúncio publicado encontrado."

        return result

    @staticmethod
    def _validate_page(page: int | None) -> int:
        if page is None:
            return 1
        if isinstance(page, bool) or not isinstance(page, int) or page < 1:
            raise ValueError("Página deve ser um inteiro positivo.")
        return page

    @staticmethod
    def _validate_search(search: str | None) -> None:
        if search is not None and not isinstance(search, str):
            raise ValueError("Busca deve ser um texto.")

    @classmethod
    def _validate_ad_type(cls, ad_type: str | None) -> None:
        if ad_type is not None and ad_type not in cls.VALID_TYPES:
            raise ValueError(
                "Tipo deve ser all, product ou service.",
            )
