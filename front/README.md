# Interface web (`front/`)

HTML, CSS e JavaScript puros, sem build nem dependências de npm. Rode cada
servidor em um terminal separado:

```bash
make backend      # API em http://127.0.0.1:5000
make front        # frontend + proxy da API em http://localhost:5173
make front-test   # testes do front (Node 18 ou mais novo)
```

O servidor do front encaminha as rotas da API para `127.0.0.1:5000`, usando a
mesma origem do navegador. Assim, login e demais chamadas funcionam também
quando o Codespaces encaminha apenas a porta 5173 para o navegador.

## Telas

`/entrar/`, `/cadastro/`, `/confirmar-email/`, `/inicio/`, `/perfil/`,
`/perfil/anunciante/`, `/anuncios/novo/`, `/anuncios/detalhes/` e
`/meus-anuncios/`. `/guia-de-estilo/` mostra os componentes do tema.

## Cabeçalho e rotas

As telas com login usam um cabeçalho único (D-035), montado por
`js/paginas/cabecalho.js` a partir de `js/dominio/navegacao.js`: logo, Início,
Meus anúncios, Meu perfil, botão **Novo anúncio** e Sair. Cada página só traz
`<header class="cabecalho" data-cabecalho>` e chama `montarCabecalho(deps)`; o
início deixa a busca e os filtros dentro do cabeçalho. Os endereços das telas
ficam em `js/dominio/rotas.js` (`ROTAS`, `rotaDetalhes`, `rotaEditarAnuncio`),
e as imagens de anúncio passam por `resolverUrlRecurso` (D-036).

## Publicação de anúncios

A tela `/anuncios/novo/` publica em `POST /api/ads`, usando o contrato já
suportado pela API: título, categoria (`produto`, `servico` ou `evento`),
descrição, estado de conservação somente para produtos e preço normalizado
com duas casas decimais ou a opção `preco_a_combinar`. O título aceita de 5 a
80 caracteres; a descrição, até 500. Os contadores e a validação contam pontos
de código Unicode, como o backend.

Na categoria `evento`, o formulário pede a data (obrigatória) e, opcionalmente,
o horário e o local (spec 015). A API confere que a data não é passada; o
prazo do evento termina no dia seguinte à data e evento não é renovado.

## Eventos em destaque no início

O `/inicio/` mostra, acima do feed, um carrossel com até 5 eventos futuros,
vindos de `GET /api/eventos-destaque` (`js/fluxos/listar_destaques.js`,
`js/paginas/destaques.js` e `css/destaques.css`). A lógica sem DOM (índice
circular, datas, quando mostrar o painel) fica em `js/dominio/destaques.js`.
O painel some com busca ou filtro; sem filtro, o feed pede
`excluir_eventos=true` para não repetir os eventos nos cards. A troca é a cada
6 s, pausa com mouse ou foco do teclado e não ocorre com "reduzir movimento".

A publicação exige sessão e perfil de anunciante completo. A página verifica
o perfil antes de exibir o formulário e a API o valida novamente ao publicar.
Como o front é estático e autentica por Bearer token no navegador, a rota da
página não tem proteção server-side; a autorização efetiva ocorre na API.
Erros de validação são associados aos campos e falhas de conexão, sessão
expirada e perfil incompleto mantêm estados distintos.

O contrato atual aceita no máximo uma foto opcional no campo `imagem`, de até
5 MiB e nos formatos JPG, PNG ou WebP. A tela mantém esse limite compatível
com a API; não envia múltiplos arquivos. Não foi adicionada uma rota de backend
nem uma nova entidade de anunciante.

Roteiro manual: entre com uma conta cujo perfil de anunciante esteja completo;
publique um produto com estado e preço, um serviço ou evento sem estado, e um
anúncio com preço `A combinar`; confira a confirmação no feed. Teste também
título abaixo de 5 e acima de 80 caracteres, descrição acima de 500, preço
inválido, formatos/tamanho de foto inválidos, perfil incompleto, sessão
expirada e indisponibilidade da API. Erros de campo devem aparecer junto ao
controle correspondente e o formulário deve preservar os dados em falhas.

## Organização

`paginas/` → `fluxos/` → `dominio/`; `adaptadores/` fala HTTP com a API (veja
[ARQUITETURA.md](../ARQUITETURA.md)). O endereço da API fica em
`js/config.js`.

## Estilo

O visual comum está em `css/tema.css`, com demonstração em `/guia-de-estilo/`.
Use as variáveis e classes do tema antes de criar estilos novos.

Quando o backend for usado por outras pessoas, `CONFIRMACAO_URL_BASE` (veja
[server/README.md](../server/README.md)) precisa apontar para o front
publicado.
