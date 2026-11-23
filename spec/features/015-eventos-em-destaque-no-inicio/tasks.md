# Tarefas: Eventos da PUC em destaque na tela inicial

Referências: `spec.md` e `plan.md` desta pasta. Só começar com a spec
**Aprovada** (D-051). Marque `[x]` ao concluir. Testes antes da implementação.

## Domain

- [x] T1: Testes de `Anuncio` com evento (data obrigatória, horário e local
  opcionais, proibidos fora de evento, limite do local) e de
  `fim_do_prazo_do_evento` em `tests/core/entities/`.
- [x] T2: Adicionar `data_evento`, `horario_evento` e `local_evento` a
  `Anuncio` e `Ad`; implementar `fim_do_prazo_do_evento`.

## Use cases

- [x] T3: Criar `EventosEmDestaqueRepository` em `server/core/interfaces/` e
  os parâmetros novos em `AdRepository` (`excluir_eventos`, campos de evento).
- [x] T4: Testes de `ListarEventosEmDestaque` (máx. 5, ordem, empate, hoje,
  passado, expirado/excluído/sem data, vazio) com fakes.
- [x] T5: Implementar `ListarEventosEmDestaque`.
- [x] T6: Testes e ajustes de `PublicarAnuncio` e `EditarAnuncio` (validação
  da data, prazo no dia seguinte ao evento, recálculo ao editar).
- [x] T7: Testes e ajustes de `RenovarAnuncio` (evento não renova),
  `ObterDetalhesAnuncio` e `ListAds` (`excluir_eventos`).

## Infra

- [x] T8: Colunas `data_evento`, `horario_evento` e `local_evento` em
  `models.py`, `schema.sql`, `server/infra/db/README.md` e testes do banco
  (D-043, skill `manter-modelagem-dados`).
- [x] T9: Testes e implementação de `listar_eventos_futuros`, campos novos e
  `excluir_eventos` no gateway SQLAlchemy.

## Web (API)

- [x] T10: Testes de `/eventos-destaque` e dos campos novos em publicação,
  edição, renovação e detalhes (`tests/api/`).
- [x] T11: Controller e presenter; ligar o use case em `server/app.py`.

## Front-end

- [x] T12: Formulário de novo anúncio/edição: "Data do evento", "Horário" e
  "Local" por categoria, erros e mensagens (CA1 a CA4).
- [x] T13: Detalhes do anúncio com data, horário e local (CA5); sem "Renovar"
  para eventos em Meus anúncios (CA9).
- [x] T14: Lógica pura do carrossel em `front/js/dominio/destaques.js` com
  testes `node --test`.
- [x] T15: Painel no início (`index.html`, `destaques.js`, `destaques.css`):
  slides só com imagem, título e data, setas, pontos, troca a cada 6 s,
  pausa, movimento reduzido, vazio, erro, acessibilidade e celular (CA10 a
  CA18, CA22 a CA24).
- [x] T16: Ocultar o painel com busca/filtro e tirar eventos do feed sem
  filtro (CA19 a CA21).
- [x] T17: (não precisou: o carrossel só serve ao início, CSS próprio) Se surgir componente comum a várias telas, levá-lo ao `tema.css` e
  ao `/guia-de-estilo/` (D-034).

## Validação

- [x] T18: `pytest` passando.
- [x] T19: `flake8` sem erros.
- [x] T20: `node --test` passando.
- [x] T21: Roteiro manual de CA1 a CA25 (desktop e celular; com e sem foto;
  0, 1, 2 e 6 ou mais eventos; evento do dia e do dia anterior). Conferido
  manualmente pela autora.
- [x] T22: Marcar a spec como Implementada.
