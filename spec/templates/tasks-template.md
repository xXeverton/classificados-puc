# Tarefas: [Nome da feature]

Referências: `spec.md` e `plan.md` desta pasta.
Marque `[x]` ao concluir. Escreva os testes antes da implementação.

## Domain

- [ ] T1: Escrever testes da entidade em `tests/core/entities/`
- [ ] T2: Implementar a entidade em `server/core/entities/`

## Use cases

- [ ] T3: Definir a interface do repositório em `server/core/interfaces/`
- [ ] T4: Escrever testes do use case em `tests/core/usecases/` (repositório em memória)
- [ ] T5: Implementar o use case em `server/core/usecases/`

## Infra

- [ ] T6: Implementar o gateway SQLAlchemy em `server/infra/gateways/`

## Web

- [ ] T7: Criar o controller em `server/api/controllers/` e conectá-lo em `server/app.py`

## Validação

- [ ] T8: `pytest` passando
- [ ] T9: `flake8` sem erros
- [ ] T10: Critérios de aceitação da `spec.md` conferidos
