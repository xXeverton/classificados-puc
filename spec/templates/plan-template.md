# Plano técnico: [Nome da feature]

Referência: `spec.md` desta pasta.

## Domain (`domain/`)

| Entidade | Atributos | Regras/validações |
|----------|-----------|-------------------|
|          |           |                   |

## Use cases (`use_cases/`)

| Use case | Entrada | Saída | Erros possíveis |
|----------|---------|-------|-----------------|
|          |         |       |                 |

Interfaces de repositório necessárias:

- `[Nome]Repository`: métodos ...

## Infra (`infra/`)

- Tabelas/colunas no SQLite:
- Implementação: `infra/repositories/[nome]_repository_sqlite.py`

## Interface web (`app/routes/`)

| Método | Rota | Use case chamado | Resposta |
|--------|------|------------------|----------|
|        |      |                  |          |

## Princípios SOLID aplicados

- ...

## Estratégia de testes

- `tests/domain/`: ...
- `tests/use_cases/`: ... (com repositório em memória)
