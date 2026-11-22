# Spec: Tela de busca e filtros do feed

- **ID**: 006
- **Status**: Rascunho
- **Data**: 2026-11-21
- **Jira**: história [PROJ-16](https://matheuscomputacaopuc.atlassian.net/browse/PROJ-16)
  (Buscar e filtrar anúncios); subtarefas
  [PROJ-46](https://matheuscomputacaopuc.atlassian.net/browse/PROJ-46)
  (barra de busca e menu retrátil de filtros) e
  [PROJ-47](https://matheuscomputacaopuc.atlassian.net/browse/PROJ-47)
  (ligar o estado dos filtros às requisições do feed)
- **Decisões gerais aplicadas**: nenhuma
- **Relacionadas**: [001](../001-visualizar-feed-anuncios/spec.md) (feed,
  busca e tipo) e [005](../005-filtrar-anuncios-categoria-preco/spec.md)
  (filtros de categoria e preço na API)

## História de usuário

**Como** comprador,
**quero** buscar por palavra-chave e filtrar o feed por tipo e faixa de preço
num menu que abro e fecho,
**para que** eu encontre rápido o que procuro sem poluir a tela.

## Critérios de aceitação

- [ ] CA1: Dado o feed aberto, quando clico em "Filtros", então abre um menu
  com o tipo (Todos, Produtos, Serviços, Eventos) e os campos de preço mínimo
  e máximo; ao clicar de novo, o menu fecha.
- [ ] CA2: Dado que escolho um tipo e uma faixa de preço, quando aplico, então
  o feed mostra só os anúncios que atendem a todos os filtros e à busca, a
  partir da página 1.
- [ ] CA3: Dado um preço inválido (texto, negativo ou mínimo maior que o
  máximo), quando aplico, então vejo a mensagem de erro no menu e o feed não
  muda.
- [ ] CA4: Dado que há filtros ativos, quando olho o botão "Filtros", então
  vejo quantos filtros estão ativos.
- [ ] CA5: Dado que há busca ou filtros ativos, quando clico em "Limpar filtros
  e busca", então tudo volta ao padrão e o feed recarrega na página 1.
- [ ] CA6: Dado que a busca e os filtros não encontram anúncios, quando o feed
  carrega, então vejo uma mensagem dizendo que nada foi encontrado com esses
  filtros.
- [ ] CA7: Dado um feed filtrado, quando recarrego a página, uso a paginação
  ou compartilho o endereço, então a busca, o tipo e a faixa de preço se
  mantêm.
- [ ] CA8: Dado um filtro de preço, quando o feed carrega, então anúncios com
  preço "a combinar" não aparecem.

## Regras de negócio

- RN1: O menu tem só tipo e faixa de preço. A "categoria" gravada pela
  publicação (PROJ-2) é sempre produto, serviço ou evento, igual ao tipo, então
  um seletor de categoria seria repetido. Ele volta quando existirem
  categorias próprias (decisão do time em 2026-11-21).
- RN2: Os preços aceitam vírgula ou ponto como separador decimal, devem ser
  maiores ou iguais a zero e o mínimo não pode passar do máximo.
- RN3: Aplicar ou limpar filtros, ou fazer uma busca, volta para a página 1.
  Trocar de página mantém busca e filtros.
- RN4: Anúncios "a combinar" não têm preço e ficam de fora quando há preço
  mínimo ou máximo (decisão do time em 2026-11-21).

## Fora do escopo

- Seletor de categoria (ver RN1).
- Busca que ignore acentos.
- Página de detalhes do anúncio (PROJ-17).

## Dúvidas em aberto

- O PO ainda precisa aprovar o visual do menu, que segue a descrição do
  wireframe da PROJ-16 (barra no topo e botão de filtro retrátil).
