# Spec: Padronizar navegação, cabeçalho e ações das telas

- **ID**: 013
- **Status**: Aprovada
- **Data**: 2026-11-23
- **Jira**: task [PROJ-54](https://matheuscomputacaopuc.atlassian.net/browse/PROJ-54)
  (épico PROJ-10); subtarefas PROJ-55 (back-end `is_owner`), PROJ-56 (rotas e
  imagens), PROJ-57 (cabeçalho único), PROJ-58 ("Ver detalhes" no painel),
  PROJ-59 ("Editar anúncio" nos detalhes) e PROJ-60 ("Cancelar" da edição)
- **Decisões gerais aplicadas**: D-004, D-030, D-031, D-032, D-034. Esta
  spec cria também D-035 e D-036 (registradas em `decisoes.md`).
- **Relacionadas**: [004-detalhar-anuncio](../004-detalhar-anuncio/spec.md),
  [007-editar-excluir-anuncio](../007-editar-excluir-anuncio/spec.md),
  [009-painel-meus-anuncios](../009-painel-meus-anuncios/spec.md) e o
  diagrama [fluxo-navegacao.md](../../fluxo-navegacao.md)

## Contexto

Uma revisão do fluxo mostrou que o cabeçalho e os botões mudam de tela para
tela: "Meus anúncios" não aparece no menu de nenhuma, "Novo anúncio" ora é
botão, ora item de menu ("Anunciar"), ora não existe, a página de detalhes
não carrega a fonte do tema e o "Cancelar" da edição leva ao feed em vez do
painel. Esta feature uniformiza isso sem criar regra de negócio nova, exceto
o botão "Editar" nos detalhes, que exige saber se quem vê é o dono do anúncio.

## História de usuário

**Como** membro logado,
**quero** encontrar os mesmos itens de navegação e os mesmos botões, no mesmo
lugar, em todas as telas,
**para que** eu me mova pela plataforma sem me perder e chegue rápido ao que
preciso (meus anúncios, novo anúncio, perfil).

## Critérios de aceitação

### Cabeçalho

- [ ] CA1: Dado qualquer tela com login (início, detalhes do anúncio, novo/editar
  anúncio, meus anúncios, perfil e perfil de anunciante), quando ela abre,
  então o cabeçalho mostra, nesta ordem: logo, "Início", "Meus anúncios",
  "Meu perfil", botão azul "Novo anúncio" e botão "Sair".
- [ ] CA2: Dado que estou em início, meus anúncios ou perfil (inclusive o
  perfil de anunciante), então o item do menu dessa tela fica marcado como
  página atual; na criação de anúncio, o marcado é o botão "Novo anúncio";
  nos detalhes e na edição, nada é marcado.
- [ ] CA3: Dado que clico no logo ou em "Início", então vou para o feed.
- [ ] CA4: Dado que clico em "Meus anúncios", então vou para o painel, mesmo
  sem ter completado o perfil de anunciante (o painel mostra listas vazias).
- [ ] CA5: Dado a tela de novo anúncio, então não existe o item de menu
  "Anunciar": o acesso é só pelo botão azul "Novo anúncio".
- [ ] CA6: Dado a tela de início, então além dos itens do CA1 ela mantém a busca
  e o botão "Filtros" no cabeçalho.
- [ ] CA7: Dado "Sair", então a sessão é encerrada e vou para a entrada, como
  hoje, em todas as telas.

### Detalhes e ações do anúncio

- [ ] CA8: Dado a tela de detalhes, então o texto usa a mesma fonte das demais
  telas.
- [ ] CA9: Dado um anúncio publicado **meu**, quando abro os detalhes, então
  vejo o botão "Editar anúncio", que leva ao formulário de edição.
- [ ] CA10: Dado um anúncio publicado **de outra pessoa**, quando abro os
  detalhes, então não vejo o botão de editar.
- [ ] CA11: Dado um anúncio **publicado** no painel "Meus anúncios", então o
  card tem o botão "Ver detalhes", que abre a tela de detalhes dele.
- [ ] CA12: Dado a edição de um anúncio (aberta pelo painel ou pelos
  detalhes), quando clico em "Cancelar", então volto para "Meus anúncios" e
  nada é salvo.
- [ ] CA13: Dado a criação de um anúncio, quando clico em "Cancelar", então
  volto para o início, como hoje.
- [ ] CA14: Dado que salvo a edição, então volto para "Meus anúncios", como hoje.

### Consistência técnica (sem mudança visível)

- [ ] CA15: Todos os endereços de tela usados pelo front vêm de uma lista única,
  sem endereços escritos soltos nas páginas.
- [ ] CA16: Todas as imagens de anúncio (feed, detalhes, painel e prévia na
  edição) são resolvidas do mesmo jeito.

## Regras de negócio

- RN1: O cabeçalho é o mesmo em todas as telas com login, em itens e ordem
  (D-035). Telas sem login (entrar, cadastro, confirmar e-mail) não o usam.
- RN2: "Novo anúncio" é sempre o botão primário azul, nunca item de menu.
- RN3: Quem não tem perfil de anunciante completo continua sendo levado a
  completá-lo ao tentar publicar (spec 003); a navegação não bloqueia o
  botão "Novo anúncio".
- RN4: Só o dono vê "Editar anúncio" nos detalhes. A API informa se quem vê é
  o dono; o front não deduz isso por conta própria.
- RN5: Os detalhes só existem para anúncios publicados (spec 004, CA10 e
  CA11). Por isso "Ver detalhes" aparece só em cards publicados.
- RN6: Rotas e imagens seguem uma única convenção no front (D-036).

## Fora do escopo

- Mudar visual, cores ou textos além dos botões citados.
- Menu hambúrguer ou outra adaptação do cabeçalho para celular além do que o
  tema já faz.
- Editar anúncios vendidos ou expirados pelos detalhes (continuam no painel).
- Tornar as telas protegidas no servidor (o front é estático; a API autoriza).

## Dúvidas resolvidas

- "Ver detalhes" só em anúncios publicados (em aberto); expirados e vendidos
  não têm o botão (CA11/RN5). Confirmado em 2026-11-23.
- Rótulos "Ver detalhes" e "Editar anúncio", estilo contorno, junto às demais
  ações. Confirmado em 2026-11-23.
- Jira: PROJ-54 e subtarefas PROJ-55 a PROJ-60.

## Dúvidas em aberto

- Nenhuma.
