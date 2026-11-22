# Tarefas: Expirar anúncios não renovados

Referências: `spec.md` e `plan.md` desta pasta. Jira: PROJ-39.
Marque `[x]` ao concluir. Escreva os testes antes da implementação.

## Domain

- [x] T1: Testes do prazo do anúncio em `tests/core/entities/test_ad.py`
  (RN1–RN5).
- [x] T2: Implementar `PUBLICATION_PERIOD`, `publication_ends_at` e
  `is_overdue` em `server/core/entities/ad.py`.

## Use cases

- [x] T3: Criar `ExpirableAdRepository` em `server/core/interfaces/`.
- [x] T4: Testes de `ExpireAds` em `tests/core/usecases/test_expire_ads.py`
  com repositório em memória (CA1–CA6).
- [x] T5: Implementar `ExpireAds` em `server/core/usecases/expire_ads.py`.

## Infra

- [x] T6: Testes de `list_published_ads` e `mark_as_expired` no gateway.
- [x] T7: Implementar os dois métodos em `AdRepositorySQLAlchemy`.

## Entrada

- [x] T8: Teste do comando `expirar-anuncios`, incluindo o anúncio sumir do
  `GET /api/ads`.
- [x] T9: Criar `server/api/comandos.py` e registrar o comando em
  `server/app.py`.

## Documentação

- [x] T10: Documentar o comando e como agendá-lo em `server/README.md`.

## Validação

- [x] T11: `pytest` passando.
- [x] T12: `flake8` sem erros.
- [x] T13: Critérios de aceitação da `spec.md` conferidos.
