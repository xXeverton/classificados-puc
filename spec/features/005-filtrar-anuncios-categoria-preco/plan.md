# Plano técnico: Filtrar anúncios por categoria e preço

Referência: `spec.md` desta pasta.

## Entities (`server/core/entities/`)

Sem mudanças: `Ad` já tem `category` e `price`.

## Use cases (`server/core/usecases/`)

| Use case | Entrada | Saída | Erros possíveis |
|----------|---------|-------|-----------------|
| `ListAds` (existente) | ganha `category`, `min_price` e `max_price`, opcionais | igual à atual | `ValueError` para preço inválido ou mínimo maior que o máximo (RN3) |

- Categoria: `strip()`; vazia vira `None` (RN1).
- Preços: aceitam `int` ou `float` (não `bool`), maiores ou iguais a zero.

Interface de repositório (`server/core/interfaces/ad_repository_interface.py`):

- `AdRepository.list_published` ganha `category`, `min_price` e `max_price`
  como parâmetros nomeados com padrão `None`, para não quebrar quem já chama.

## Infra (`server/infra/`)

- Sem mudança de tabela.
- `AdRepositorySQLAlchemy.list_published` adiciona os filtros:
  `lower(category) = lower(:category)`, `price >= :min_price` e
  `price <= :max_price`.

## Interface web (`server/api/controllers/ads_controller.py`)

| Método | Rota | Use case chamado | Resposta |
|--------|------|------------------|----------|
| GET | `/api/ads?category=&min_price=&max_price=` (além de `page`, `search` e `type`) | `ListAds` | `200` com o feed; `400` com mensagem para preço inválido |

O controller converte `min_price` e `max_price` para número; texto que não é
número responde `400`.

## Princípios SOLID aplicados

- **O**: os filtros novos entram como parâmetros opcionais, sem mudar o
  comportamento de quem não os usa.
- **D**: `ListAds` continua dependendo só da interface `AdRepository`.

## Estratégia de testes

- `tests/core/usecases/test_list_ads.py`: repassa os filtros ao repositório;
  categoria vazia vira `None`; erros de preço (CA5).
- `tests/infra/gateways/test_ad_repository_filters.py`: categoria sem
  diferenciar maiúsculas, limites inclusivos, combinação com busca e tipo.
- `tests/api/test_ads_controller.py`: parâmetros pela URL (CA1–CA4, CA6) e
  `400` para preço inválido (CA5).
