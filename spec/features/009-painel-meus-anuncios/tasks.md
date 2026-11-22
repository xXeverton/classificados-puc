# Tarefas: Painel "Meus Anúncios"

Referências: `spec.md`, `plan.md` e Jira PROJ-37.
Marque `[x]` ao concluir. Escreva os testes antes da implementação.

Status atual: **Aprovada**.

## Contrato

- [x] T1: Definir `GET /api/ads?owner=me&page={page}`, somente anúncios
  publicados, ordenação por `created_at DESC` e paginação de 20 itens.
- [x] T2: Definir Editar, Excluir e Renovar como ações dos cards.
- [x] T3: Definir `POST /api/ads/<id>/renovar` para anúncio expirado próprio.

## Use case e persistência

- [x] T4: Escrever testes do use case com repositório em memória.
- [x] T5: Implementar o filtro `owner=me` na consulta publicada.
- [x] T6: Implementar o método no gateway SQLAlchemy.

## API

- [x] T7: Escrever testes do controller para sucesso, lista vazia, autenticação
  e falha.
- [x] T8: Ampliar `GET /api/ads` e montar o use case em `server/app.py`.

## Front-end

- [x] T9: Escrever testes dos fluxos e das funções puras do painel.
- [x] T10: Criar HTML, CSS e módulos da tela seguindo o tema e o guia de estilo.
- [x] T11: Integrar a tela ao adaptador HTTP e aos estados de sessão e erro.
- [x] T12: Adicionar o link “Meus anúncios” no perfil.
- [x] T13: Integrar Editar e Excluir aos contratos já existentes.
- [x] T14: Integrar Renovar pelo contrato criado nesta feature.
- [x] T19: Fazer o formulário de edição iniciar com os dados do anúncio.
- [x] T20: Ajustar e validar a responsividade dos cards em telas estreitas.

## Validação

- [ ] T15: `pytest` completo passa; o ambiente atual bloqueia apenas o teste
  de symlink no Windows.
- [x] T16: `node --test` do front passou.
- [x] T17: Critérios de aceitação da `spec.md` conferidos nos testes afetados.
- [ ] T18: `make check` completo passa; lint passou e pytest teve uma falha
  ambiental de privilégio de symlink no Windows.
