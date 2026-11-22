# Tarefas: Filtrar anúncios por categoria e preço

Referências: `spec.md` e `plan.md` desta pasta. Jira: PROJ-45.
Marque `[x]` ao concluir. Escreva os testes antes da implementação.

## Use cases

- [x] T1: Testes de `ListAds` com categoria e faixa de preço, incluindo os
  erros de preço (CA5).
- [x] T2: Ampliar `AdRepository.list_published` e o `ListAds`.

## Infra

- [x] T3: Testes do gateway para categoria, limites de preço e combinação.
- [x] T4: Implementar os filtros em `AdRepositorySQLAlchemy`.

## Web

- [x] T5: Testes de API para os parâmetros novos e o `400`.
- [x] T6: Ler `category`, `min_price` e `max_price` no `ads_controller`.

## Validação

- [x] T7: `pytest` passando.
- [x] T8: `flake8` sem erros.
- [x] T9: Critérios de aceitação da `spec.md` conferidos.
