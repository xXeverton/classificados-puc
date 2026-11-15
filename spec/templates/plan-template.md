# Plano técnico: [Nome da feature]

Referência: `spec.md` desta pasta.

## Entities (`server/core/entities/`)

| Entidade | Atributos | Regras/validações |
|----------|-----------|-------------------|
|          |           |                   |

## Use cases (`server/core/usecases/`)

| Use case | Entrada | Saída | Erros possíveis |
|----------|---------|-------|-----------------|
|          |         |       |                 |

Interfaces de repositório necessárias (`server/core/interfaces/`):

- `[Nome]Repository`: métodos ...

## Infra (`server/infra/`)

- Tabelas/colunas no SQLite:
- Modelo SQLAlchemy: `server/infra/db/models.py`
- Implementação: `server/infra/gateways/[nome]_repository_sqlalchemy.py`

## Interface web (`server/api/controllers/`)

| Método | Rota | Use case chamado | Resposta |
|--------|------|------------------|----------|
|        |      |                  |          |

## Princípios SOLID aplicados

- ...

## Estratégia de testes

- `tests/core/entities/`: ...
- `tests/core/usecases/`: ... (com repositório em memória)
