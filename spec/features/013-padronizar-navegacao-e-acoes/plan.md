# Plano técnico: Padronizar navegação, cabeçalho e ações das telas

Referência: `spec.md` desta pasta. A maior parte é front (D-030: HTML, CSS e
JS puros, sem build); há uma mudança pequena no backend (RN4).

## Front

### Rotas e imagens (CA15, CA16, D-036)

- `front/js/dominio/rotas.js` (novo, sem DOM): `ROTAS` (movida de
  `paginas/comum.js`, com `detalhes` incluída) e as funções `rotaDetalhes(id)`
  e `rotaEditarAnuncio(id)`. `comum.js` reexporta `ROTAS` para não quebrar
  importações.
- Substituir endereços soltos: `"/entrar/"` em `detalhes_anuncio.js`,
  `/anuncios/novo/?editar=` em `meus_anuncios.js`, `detalhesUrl` em
  `dominio/feed.js`.
- Imagens: `meus_anuncios.js` e a prévia da edição
  (`fluxos/anuncio_edicao.js` → `anuncios_novo.js`) passam por
  `resolverUrlRecurso`, como início e detalhes.

### Cabeçalho único (CA1 a CA7, D-035)

- `front/js/dominio/navegacao.js` (novo, sem DOM): `ITENS_DO_CABECALHO`
  (rótulo, rota, chave) e `itemAtual(caminho)`, que devolve a chave do item
  marcado (`inicio`, `meus-anuncios`, `perfil`, `novo-anuncio`) ou `null`
  (detalhes e edição), tratando `/perfil/anunciante/` como `perfil`.
- `front/js/paginas/cabecalho.js` (novo): monta o cabeçalho dentro de
  `<header class="cabecalho" data-cabecalho>` com `createElement` e
  `textContent` (D-031): logo, conteúdo extra da página (a busca e o botão
  Filtros do início ficam no HTML, entre o logo e o menu), menu, botão
  "Novo anúncio" e "Sair" (`ligarBotaoSair`). Marca `aria-current="page"`.
- As 7 telas com login trocam o `<header>` escrito à mão por esse marcador e
  importam `cabecalho.js`; o item "Anunciar" desaparece.
- Estilo: reaproveita `.cabecalho`, `.navegacao` e `.botao` do `tema.css`; só
  se faltar algo, entra no `tema.css` **e** no `/guia-de-estilo/`, que
  passa a mostrar o cabeçalho completo (D-034).
- `anuncios/detalhes/index.html`: adicionar o `<link>` da fonte (CA8).

### Ações do anúncio (CA9 a CA14)

- Painel: `acoesDoAnuncio(status)` em `dominio/meus_anuncios.js` ganha a ação
  `detalhes` ("Ver detalhes", link) só para `published` (RN5);
  `criarBotaoDeAcao` a renderiza como `<a>` para `rotaDetalhes(id)`.
- Detalhes: se a resposta indicar `is_owner`, mostrar "Editar anúncio" (link
  para `rotaEditarAnuncio(id)`) no painel do anúncio.
- Edição (`anuncios_novo.js`): em modo edição, o link "Cancelar" aponta para
  `ROTAS.meusAnuncios`; na criação continua em `ROTAS.inicio`.

## Backend (CA9, CA10, RN4)

- `server/core/entities/ad_details.py`: `AdDetails` ganha `is_owner: bool`
  (padrão `False`), calculado no use case, sem HTTP.
- `server/core/usecases/obter_detalhes_anuncio.py`: define
  `is_owner = ad.usuario_id == usuario.id`.
- `server/api/presenters/ad_presenter.py`: `AdDetailsViewSchema` ganha
  `is_owner: bool` e o presenter o preenche. Mudança compatível: campo novo,
  nada removido. Nenhuma tabela muda.

## Princípios aplicados

- A regra de "quem é dono" fica no use case; o presenter só traduz (Clean
  Architecture, constituição §1).
- Lógica do cabeçalho e das rotas fica em `dominio/`, testável sem DOM;
  `paginas/` só monta elementos.
- Uma fonte única para rotas e para o cabeçalho, sem abstração especulativa.

## Estratégia de testes

- `tests/core/usecases/test_obter_detalhes_anuncio.py`: `is_owner` verdadeiro
  para o dono e falso para outra pessoa.
- `tests/api/test_ads_controller.py`: a resposta de detalhes traz `is_owner`.
- `front/tests/navegacao.test.js` (novo): itens e ordem do cabeçalho;
  `itemAtual` para cada caminho, incluindo `/perfil/anunciante/` e detalhes.
- `front/tests/rotas.test.js` (novo): `rotaDetalhes` e `rotaEditarAnuncio`
  com `id` escapado.
- `front/tests/meus_anuncios.test.js` e `feed.test.js`: "Ver detalhes" só em
  publicados; `detalhesUrl` continua `/anuncios/detalhes/?id=<id>`.
- Roteiro manual no navegador para CA1 a CA16, em tela larga e no celular
  (sem rolagem horizontal, D-032).
