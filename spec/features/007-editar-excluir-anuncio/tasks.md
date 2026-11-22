# Tarefas: Editar e excluir anúncio

Referências: `spec.md` e `plan.md` desta pasta. Jira: PROJ-38.
Marque `[x]` ao concluir. Escreva os testes antes da implementação.

## Use cases

- [x] T1: Criar a interface `AnuncioEditavelRepositoryInterface` e os erros
  novos.
- [x] T2: Testes de `EditarAnuncio` e `ExcluirAnuncio` com repositório em
  memória.
- [x] T3: Implementar os dois use cases e ampliar `Ad` com dono e foto.

## Infra

- [x] T4: Testes do gateway para buscar, atualizar e excluir.
- [x] T5: Implementar os métodos em `AdRepositorySQLAlchemy`.

## Web

- [x] T6: Testes de API de `PUT` e `DELETE /api/ads/<id>`.
- [x] T7: Criar as rotas e montar os use cases em `server/app.py`.

## Validação

- [x] T8: `pytest` passando.
- [x] T9: `flake8` sem erros.
- [x] T10: Critérios de aceitação da `spec.md` conferidos.
