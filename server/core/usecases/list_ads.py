"""Use case for listing advertisements available in the feed."""

from math import ceil, isfinite

from server.core.entities.usuario import Usuario
from server.core.interfaces.ad_repository_interface import AdRepository
from server.core.usecases.erros import ErroDeCasoDeUso


class ListAds:
    """List published advertisements for an authenticated user."""

    PER_PAGE = 20
    VALID_TYPES = {"all", "product", "service", "event"}

    def __init__(self, repository: AdRepository):
        self.repository = repository

    def execute(
        self,
        usuario: Usuario | None,
        page: int | None = None,
        search: str | None = None,
        ad_type: str | None = None,
        category: str | None = None,
        min_price: float | None = None,
        max_price: float | None = None,
    ) -> dict[str, object]:
        if usuario is None:
            raise ErroDeCasoDeUso(
                "Usuário não autenticado.",
            )

        page = self._validate_page(page)
        self._validate_search(search)
        self._validate_ad_type(ad_type)
        category = self._normalize_category(category)
        self._validate_price_range(min_price, max_price)

        # The requested page is kept even with a search or filter, so the
        # user can page through results. Going back to the first page when
        # a search or filter changes (RN11) is the client's job: only it
        # knows whether the filter changed or the user just turned a page.
        items, total_items = self.repository.list_published(
            page=page,
            per_page=self.PER_PAGE,
            search=search,
            ad_type=ad_type,
            category=category,
            min_price=min_price,
            max_price=max_price,
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
                "Tipo deve ser all, product, service ou event.",
            )

    @staticmethod
    def _normalize_category(category: str | None) -> str | None:
        if category is None:
            return None
        if not isinstance(category, str):
            raise ValueError("Categoria deve ser um texto.")
        return category.strip() or None

    @classmethod
    def _validate_price_range(
        cls,
        min_price: float | None,
        max_price: float | None,
    ) -> None:
        cls._validate_price(min_price, "Preço mínimo")
        cls._validate_price(max_price, "Preço máximo")
        if (
            min_price is not None
            and max_price is not None
            and min_price > max_price
        ):
            raise ValueError(
                "Preço mínimo não pode ser maior que o máximo.",
            )

    @staticmethod
    def _validate_price(price: float | None, label: str) -> None:
        if price is None:
            return
        if (
            isinstance(price, bool)
            or not isinstance(price, (int, float))
            or not isfinite(price)
        ):
            raise ValueError(f"{label} deve ser um número.")
        if price < 0:
            raise ValueError(f"{label} não pode ser negativo.")
