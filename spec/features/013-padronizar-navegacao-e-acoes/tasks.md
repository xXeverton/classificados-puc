# Tarefas: Padronizar navegação, cabeçalho e ações das telas

Referências: `spec.md` e `plan.md` desta pasta. Jira: PROJ-54. Só começar
com a spec **Aprovada** (D-051). Testes antes da implementação. Blocos
separados por subtarefa (D-050).

## PROJ-55 — [Back-end] `is_owner` nos detalhes

- [x] T1: Testes do use case e do controller para `is_owner` (dono e não dono).
- [x] T2: `AdDetails`, `ObterDetalhesAnuncio` e presenter com `is_owner`.
- [x] T3: `pytest` e `flake8` passando.

## PROJ-56 — [Front-end] Rotas e imagens

- [x] T4: Testes de `rotas.js` (`rotaDetalhes`, `rotaEditarAnuncio`).
- [x] T5: Criar `dominio/rotas.js`, reexportar em `comum.js` e trocar os
  endereços soltos (detalhes, meus anúncios, feed).
- [x] T6: Passar imagens do painel e da prévia de edição por `resolverUrlRecurso`.

## PROJ-57 — [Front-end] Cabeçalho único

- [ ] T7: Testes de `dominio/navegacao.js` (itens, ordem, `itemAtual`).
- [ ] T8: Implementar `navegacao.js` e `paginas/cabecalho.js`.
- [ ] T9: Aplicar o cabeçalho nas 7 telas (início mantém busca e Filtros),
  remover "Anunciar" e adicionar a fonte em detalhes.
- [ ] T10: Mostrar o cabeçalho completo em `/guia-de-estilo/`.

## PROJ-58 — [Front-end] "Ver detalhes" no painel

- [ ] T11: Testes: "Ver detalhes" só em publicados (`acoesDoAnuncio`).
- [ ] T12: "Ver detalhes" no card do painel.

## PROJ-59 — [Front-end] "Editar anúncio" nos detalhes

- [ ] T13: "Editar anúncio" nos detalhes quando `is_owner` (depende de PROJ-55).

## PROJ-60 — [Front-end] "Cancelar" da edição

- [ ] T14: "Cancelar" da edição volta para Meus anúncios.

## Validação

- [ ] T15: `node --test` e `pytest` passando; `flake8` sem erros.
- [ ] T16: Roteiro manual no navegador (CA1 a CA16), desktop e celular.
- [ ] T17: Atualizar `front/README.md` (lista de telas e cabeçalho) e marcar a
  spec como Implementada.
