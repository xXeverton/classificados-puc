# Spec: Filtrar anúncios por categoria e preço

- **ID**: 005
- **Status**: Rascunho
- **Data**: 2026-11-21
- **Jira**: história [PROJ-16](https://matheuscomputacaopuc.atlassian.net/browse/PROJ-16)
  (Buscar e filtrar anúncios); subtarefa
  [PROJ-45](https://matheuscomputacaopuc.atlassian.net/browse/PROJ-45)
  (parâmetros de busca e filtro no back-end)
- **Decisões gerais aplicadas**: nenhuma
- **Relacionada**: [001-visualizar-feed-anuncios](../001-visualizar-feed-anuncios/spec.md),
  que já entrega a busca por texto e o filtro de tipo e deixava categoria e
  preço fora do escopo.

## História de usuário

**Como** comprador,
**quero** filtrar os anúncios do feed por categoria e por faixa de preço,
**para que** eu encontre rápido o item que procuro.

Esta spec cobre só o back-end da PROJ-45. As telas ficam na PROJ-46 e na
PROJ-47.

## Critérios de aceitação

- [ ] CA1: Dado que escolho a categoria "Eletrônicos", quando aplico o filtro,
  então só aparecem anúncios dessa categoria.
- [ ] CA2: Dado que informo um preço mínimo, quando aplico o filtro, então só
  aparecem anúncios com preço maior ou igual a ele.
- [ ] CA3: Dado que informo um preço máximo, quando aplico o filtro, então só
  aparecem anúncios com preço menor ou igual a ele.
- [ ] CA4: Dado que combino busca por texto, tipo, categoria e faixa de preço,
  quando aplico, então só aparecem anúncios que atendem a todos os filtros,
  na ordem e na paginação do feed.
- [ ] CA5: Dado um preço mínimo maior que o máximo, ou um preço negativo ou
  que não é número, quando aplico o filtro, então vejo uma mensagem de erro e
  nenhum anúncio é filtrado.
- [ ] CA6: Dado que nenhum anúncio atende aos filtros, quando aplico, então
  recebo uma lista vazia com a mensagem de feed vazio.

## Regras de negócio

- RN1: A categoria é comparada pelo nome inteiro, sem diferenciar maiúsculas
  e minúsculas e ignorando espaços nas pontas. Categoria vazia equivale a não
  filtrar.
- RN2: Os limites de preço são inclusivos e podem ser usados sozinhos ou
  juntos.
- RN3: Preços devem ser números maiores ou iguais a zero, e o mínimo não pode
  passar do máximo.
- RN4: Os filtros novos se combinam com a busca por texto e com o filtro de
  tipo da spec 001 e mantêm a ordenação (mais recente primeiro) e as 20
  posições por página.

## Fora do escopo

- Tipo "Evento": exige mudar o banco e o formulário de publicação (PROJ-2).
- Lista fixa de categorias: o filtro aceita qualquer nome; a lista que a tela
  oferece é decisão do PO.
- Anúncios com preço "a combinar": hoje todo anúncio tem preço obrigatório.
- Telas da busca e dos filtros (PROJ-46 e PROJ-47).

## Dúvidas em aberto

- O PO precisa definir a lista de categorias e se "Evento" vira um tipo.
- Quando o preço "a combinar" existir, decidir se esses anúncios aparecem
  quando há filtro de preço.
- A comparação sem diferenciar maiúsculas usa o `lower()` do SQLite, que só
  converte letras sem acento. "ELETRÔNICOS" encontra "Eletrônicos", mas uma
  categoria gravada como "ÓCULOS" não seria encontrada por "óculos".
