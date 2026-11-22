# Tarefas: Painel "Meus Anúncios"

Referências: `spec.md`, `plan.md` e Jira PROJ-37.
Marque `[x]` ao concluir. Escreva os testes antes da implementação.

Status atual: **Rascunho; não implementar antes da aprovação explícita da
spec**.

## Contrato

- [x] T1: Definir `GET /api/ads?owner=me&page={page}`, somente anúncios
  publicados, ordenação por `created_at DESC` e paginação de 20 itens.
- [x] T2: Definir Editar, Excluir e Renovar como ações dos cards.
- [ ] T3: Confirmar o contrato HTTP da renovação da PROJ-40 antes de ligar a
  ação Renovar.

## Use case e persistência

- [ ] T4: Escrever testes do use case com repositório em memória.
- [ ] T5: Implementar o filtro `owner=me` na consulta publicada.
- [ ] T6: Implementar o método no gateway SQLAlchemy.

## API

- [ ] T7: Escrever testes do controller para sucesso, lista vazia, autenticação
  e falha.
- [ ] T8: Ampliar `GET /api/ads` e montar o use case em `server/app.py`.

## Front-end

- [ ] T9: Escrever testes dos fluxos e das funções puras do painel.
- [ ] T10: Criar HTML, CSS e módulos da tela seguindo o tema e o guia de estilo.
- [ ] T11: Integrar a tela ao adaptador HTTP e aos estados de sessão e erro.
- [ ] T12: Adicionar o link “Meus anúncios” no perfil.
- [ ] T13: Integrar Editar e Excluir aos contratos já existentes.
- [ ] T14: Integrar Renovar após a confirmação do contrato da PROJ-40.

## Validação

- [ ] T15: `pytest` passando.
- [ ] T16: `npm test` ou `make front-test` passando.
- [ ] T17: Critérios de aceitação da `spec.md` conferidos.
- [ ] T18: `make check` executado ou falhas de ambiente explicitadas.
