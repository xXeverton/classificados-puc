# Tarefas: Aplicar o guia de estilo na tela de novo anúncio

Referências: `spec.md` e `plan.md` desta pasta. Jira: PROJ-61. Só começar
com a spec **Aprovada** (D-051).

## PROJ-61 — [Front-end] Guia de estilo na tela de novo anúncio

- [x] T1: Reestruturar `front/anuncios/novo/index.html`: `painel`, seções com
  título, `opcoes` no preço, `campo__opcional` na foto, área "Sem foto",
  rodapé ajuda/contador. Manter todos os IDs (RN1).
- [x] T2: Ajustar `front/css/anuncios.css`: largura da página, seções, prévia
  da foto, rodapé do campo, celular; remover `.opcoes-preco*`; só variáveis
  do tema.
- [x] T3: Se preciso, alternar "Sem foto"/prévia em `anuncios_novo.js` (sem
  mudar regras).
- [x] T4: (não precisou: nenhum padrão novo serve a outras telas) Se algum padrão novo servir a várias telas, levá-lo ao `tema.css` e
  ao `/guia-de-estilo/`.

## Validação

- [x] T5: `node --test` passando.
- [ ] T6: Roteiro manual (CA1 a CA12): criação e edição, com e sem foto, os
  dois tipos de preço, erros, falha de conexão, desktop e celular.
- [ ] T7: Marcar a spec como Implementada e fechar PROJ-61.
