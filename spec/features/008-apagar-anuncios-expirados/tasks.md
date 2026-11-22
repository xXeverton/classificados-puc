# Tarefas: Apagar anúncios expirados há mais de 30 dias

Referências: `spec.md` e `plan.md` desta pasta. Jira: PROJ-41.
Marque `[x]` ao concluir. Escreva os testes antes da implementação.

## Domain

- [x] T1: Testes de `Ad.can_be_deleted` em `tests/core/entities/test_ad.py`.
- [x] T2: Implementar `RETENTION_AFTER_EXPIRY` e `can_be_deleted`.

## Use cases

- [x] T3: Criar a interface `DeletableAdRepository`.
- [x] T4: Testes de `DeleteExpiredAds` (CA1–CA5).
- [x] T5: Implementar `DeleteExpiredAds`.

## Infra

- [x] T6: Testes e implementação de `list_expired_ads` e `delete_expired`.

## Entrada

- [x] T7: Teste do comando `apagar-anuncios-expirados`, com foto.
- [x] T8: Criar o comando e registrá-lo em `server/app.py`.

## Documentação

- [x] T9: Documentar o comando em `server/README.md`.

## Validação

- [x] T10: `pytest` e `flake8` passando.
- [x] T11: Critérios de aceitação conferidos.
