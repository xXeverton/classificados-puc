# Spec: Eventos da PUC em destaque na tela inicial

- **ID**: 015
- **Status**: Implementada
- **Data**: 2026-11-23
- **Decisões gerais aplicadas**: D-001, D-004, D-007, D-008, D-009, D-010,
  D-012, D-020, D-022, D-023, D-025, D-030, D-031, D-032, D-033, D-034, D-035,
  D-036, D-043
- **Relacionadas**: [001-visualizar-feed-anuncios](../001-visualizar-feed-anuncios/spec.md),
  [006-tela-busca-filtros](../006-tela-busca-filtros/spec.md),
  [007-editar-excluir-anuncio](../007-editar-excluir-anuncio/spec.md),
  [008-apagar-anuncios-expirados](../008-apagar-anuncios-expirados/spec.md),
  [010-expirar-anuncios](../010-expirar-anuncios/spec.md),
  [014-estilizar-tela-novo-anuncio](../014-estilizar-tela-novo-anuncio/spec.md)

## Contexto

Hoje o início (`/inicio/`) mostra só a busca, os filtros e o feed de anúncios.
Eventos já existem como um tipo de anúncio ("Evento"), mas não têm data nem
destaque: aparecem misturados aos produtos, por ordem de criação.

A referência visual é a página inicial do site da PUC-Rio: uma faixa grande no
topo, em carrossel (imagem, título, subtítulo e pontos de navegação), e o
conteúdo comum logo abaixo. Aqui, a faixa mostra os **eventos da PUC** e os
**produtos** continuam abaixo, como hoje.

Os eventos **não** têm uma origem separada: são anúncios da categoria
"Evento", criados pelo mesmo formulário de novo anúncio, que passa a pedir
data, horário e local quando essa categoria é escolhida (D-008).

## História de usuário

**Como** membro da comunidade PUC,
**quero** ver, ao abrir a plataforma, os próximos eventos da PUC em destaque
e, logo abaixo, os produtos anunciados,
**para que** eu não perca o que está acontecendo na universidade e encontre o
que preciso no mesmo lugar.

## Critérios de aceitação

### Cadastro do evento

- [x] CA1: Dado o formulário de novo anúncio, quando a pessoa escolhe a
  categoria "Evento", então aparecem os campos "Data do evento"
  (obrigatório), "Horário" (opcional) e "Local" (opcional), e some o campo que
  só vale para produto (estado de conservação).
- [x] CA2: Dado a categoria "Evento" sem data, ou com data já passada, quando
  a pessoa tenta publicar, então o anúncio não é publicado e o campo mostra o
  erro correspondente.
- [x] CA3: Dado uma categoria diferente de "Evento", então os campos de data,
  horário e local não são mostrados e nada disso é guardado.
- [x] CA4: Dado um evento já publicado, quando o dono o edita, então vê a
  data, o horário e o local atuais, pode alterá-los, e vale a mesma regra do
  CA2.
- [x] CA5: Dado a tela de detalhes de um evento, então ela mostra a data e,
  quando informados, o horário e o local.

- [x] CA5a: Dado a categoria "Evento", então o preço ganha a opção "Sem preço"
  (além de "Informar preço" e "A combinar"); ao escolhê-la, o campo de valor
  some e o anúncio é publicado sem nenhum preço.
- [x] CA5b: Dado um evento "Sem preço", então nem o card do feed, nem a tela de
  detalhes, nem "Meus anúncios" mostram preço (nem "A combinar"), e ele não
  aparece quando há filtro de preço.
- [x] CA5c: Dado produto ou serviço, então a opção "Sem preço" não existe e a
  API a recusa.

### Prazo do evento

- [x] CA6: Dado um evento publicado, quando chega o dia seguinte à data do
  evento, então o anúncio expira e deixa de aparecer no painel, no feed e no
  filtro "Eventos"; durante o dia do evento, ele continua publicado (D-009).
- [x] CA7: Dado um evento com data a mais de 30 dias, então ele continua
  publicado até o dia seguinte ao evento, sem precisar de renovação (D-009).
- [x] CA8: Dado o dono editar a data de um evento publicado, então o prazo
  passa a terminar no dia seguinte à nova data.
- [x] CA9: Dado um evento em "Meus anúncios", então a ação "Renovar" não
  aparece para ele.

- [x] CA9a: Dado um evento em "Meus anúncios", então em vez de "Marcar como
  vendido" aparece "Marcar como concluído"; concluído, ele sai do feed e dos
  destaques, vai para a seção "Vendidos e concluídos" e pode ser reativado.

### Painel de destaques

- [x] CA10: Dado que existam eventos publicados com data de hoje ou futura,
  quando a pessoa abre o início, então o painel de destaques aparece no topo,
  acima da busca e do feed, começando pelo evento mais próximo.
- [x] CA11: Dado o painel, então cada destaque mostra só a imagem do evento,
  o título e a data; horário e local ficam só nos detalhes. Sem foto, o
  destaque mostra um fundo padrão do tema, sem quebrar o layout.
- [x] CA12: Dado que existam mais de 5 eventos futuros, então o painel mostra
  só os 5 com data mais próxima; em empate de data, o publicado primeiro vem
  antes.
- [x] CA13: Dado que existam de 2 a 5 destaques, então o painel funciona como
  carrossel: troca sozinho a cada 6 segundos, e a pessoa pode trocar por setas
  e por pontos (um ponto por destaque, com o atual marcado).
- [x] CA14: Dado que a pessoa passe o mouse ou o foco do teclado sobre o
  painel, então a troca automática pausa; dado que o aparelho peça menos
  movimento, então não há troca automática.
- [x] CA15: Dado que exista só 1 evento futuro, então o painel mostra esse
  evento sem setas, pontos nem troca automática.
- [x] CA16: Dado um destaque, quando a pessoa o clica, então abre a tela de
  detalhes do anúncio do evento.
- [x] CA17: Dado que não haja eventos futuros publicados, então o painel não
  aparece e o início fica como hoje, sem espaço vazio nem mensagem de erro.
- [x] CA18: Dado um evento expirado ou excluído, ou um evento antigo sem data,
  então ele não aparece no painel.

### Produtos abaixo

- [x] CA19: Dado o início sem busca nem filtro, então o feed de anúncios
  aparece abaixo do painel, com a busca, os filtros, os cards e a paginação
  como hoje.
- [x] CA20: Dado que a pessoa use a busca ou um filtro (tipo, categoria,
  preço), então o painel de destaques fica oculto e só o resultado aparece; ao
  limpar, o painel volta.
- [x] CA21: Dado o feed sem filtro, então os eventos não se repetem nos cards
  de baixo: aparecem só no painel. O filtro "Eventos" continua listando os
  eventos publicados.

### Comportamento geral

- [x] CA22: Dado uma falha ao carregar os destaques (conexão ou erro), então o
  feed abaixo continua funcionando e o painel some ou mostra um aviso curto,
  sem impedir o uso da tela (D-032).
- [x] CA23: Dado um celular (até 480 px), então não há rolagem horizontal, o
  painel ocupa a largura toda, o texto continua legível sobre a imagem e as
  setas e os pontos têm área de toque confortável.
- [x] CA24: Dado o uso só pelo teclado e por leitor de tela, então o painel
  tem nome ("Eventos em destaque"), setas e pontos têm rótulos (ex.: "Evento
  2 de 5") e o destaque atual é anunciado.
- [x] CA25: Dado uma sessão inválida ou ausente, então a lista de destaques
  não é entregue (D-004).

## Regras de negócio

- RN1: Evento é um anúncio da categoria "Evento" (D-008) e segue o ciclo dos
  demais (publicado, expirado, excluído; exclusão 30 dias após expirar, spec
  008), exceto pelo prazo (RN4).
- RN2: Evento exige **data**, de hoje em diante no momento de publicar ou
  editar. **Horário** (hora e minuto) e **local** (até 80 caracteres) são
  opcionais.
- RN3: Outras categorias não têm data, horário nem local de evento.
- RN3a: Só evento pode ficar **sem preço**: não tem valor nem "a combinar".
  As três opções de preço são excludentes.
- RN4: O prazo de um evento termina no **início do dia seguinte à data do
  evento**, no lugar dos 30 dias; evento não é renovado (D-009).
- RN5: Eventos publicados antes desta feature, sem data, continuam com o prazo
  de 30 dias e nunca entram no painel, até serem editados com data.
- RN6: O painel mostra no máximo **5** eventos publicados com data de hoje ou
  futura, do mais próximo ao mais distante; em empate, o publicado primeiro.
- RN7: O carrossel troca de destaque a cada **6 segundos**.
- RN8: "Hoje" e "dia seguinte" seguem o calendário de Brasília. As datas e
  horas do sistema continuam em UTC (D-023).
- RN9: Pode publicar evento qualquer membro com perfil de anunciante completo
  (D-007, D-010). Não há conferência de que o evento é oficial da PUC: vale a
  confiança do e-mail institucional (D-001).
- RN10: A imagem do evento segue a regra de fotos do anúncio (D-012, D-025).
- RN11: Textos do evento são exibidos só como texto (D-031).

## Fora do escopo

- Importar eventos do site da PUC-Rio ou de outras fontes.
- Papéis de administração, moderação ou selo de "evento oficial" (D-007).
- Horário de término, evento de vários dias, recorrência e mapa do local.
- Reativar um evento que já expirou.
- Confirmação de presença, lembretes e notificações.
- Ordenação manual dos destaques ou destaque pago.
- Página própria com todos os eventos (vale o filtro "Eventos").
- Mudar o visual dos cards de produtos, da busca e dos filtros.

## Dúvidas em aberto

- Nenhuma. Respostas de 2026-11-23: eventos antigos sem data ficam fora do
  painel (RN5); painel oculto com busca/filtro e eventos fora dos cards do feed
  sem filtro (CA20, CA21); horário e local só nos detalhes, não no carrossel
  (CA5, CA11); evento expira no dia seguinte (D-009); troca a cada 6 s (RN7).
