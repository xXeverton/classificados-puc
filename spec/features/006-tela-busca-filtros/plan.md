# Plano técnico: Tela de busca e filtros do feed

Referência: `spec.md` desta pasta.

## Domínio do front (`front/js/dominio/feed.js`)

- `parametrosDoFeed` passa a ler `min_price` e `max_price` da URL
  (`minPrice`/`maxPrice`, `null` quando ausentes ou inválidos).
- `montarParametrosFeed` inclui `min_price` e `max_price` quando há valor.
  Página, URL do navegador e requisição à API usam a mesma função (CA7).
- `lerFaixaDePreco(textoMin, textoMax)`: converte o que a pessoa digitou
  (vírgula ou ponto) e devolve `{ minPrice, maxPrice }` ou `{ erro }` (RN2).
- `contarFiltrosAtivos(params)`: tipo diferente de "Todos" e cada limite de
  preço contam 1 (CA4).
- `paramsSemFiltros()`: estado padrão, na página 1 (CA5).
- `mensagemDeFeedVazio(params, mensagemDaApi)`: com busca ou filtro ativo,
  "Nenhum anúncio encontrado com esses filtros."; sem filtros, a mensagem da
  API (CA6).

## Tela (`front/inicio/index.html`, `front/js/paginas/inicio.js`)

- Botão "Filtros" no cabeçalho, ao lado da busca, com `aria-expanded`,
  `aria-controls` e contador de filtros ativos.
- Menu retrátil (`form#painel-filtros`) com os botões de tipo (os mesmos do
  feed atual, movidos para dentro do menu), preço mínimo e máximo
  (`inputmode="decimal"`), mensagem de erro e o botão "Aplicar filtros".
- Botão "Limpar filtros e busca", visível só quando há busca ou filtro.
- Os tipos só valem ao aplicar, junto com o preço.
- Estilos em `front/css/tema.css`, com as variáveis do tema.

## Back-end (`server/infra/gateways/ad_repository_sqlalchemy.py`)

- Com `min_price` ou `max_price`, a consulta exclui `preco_a_combinar` (RN4).

## Estratégia de testes

- `front/tests/feed.test.js`: parâmetros da URL, URL da API, faixa de preço,
  contador, limpar e mensagem de feed vazio.
- `tests/infra/gateways/test_ad_repository_filters.py`: "a combinar" fora com
  filtro de preço e presente sem ele.
- Teste no navegador do fluxo completo (CA1–CA8).
