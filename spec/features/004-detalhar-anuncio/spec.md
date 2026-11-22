# Spec: Detalhar anúncio

- **ID**: 004
- **Jira**: história [PROJ-17](https://matheuscomputacaopuc.atlassian.net/browse/PROJ-17);
  subtarefas [PROJ-48](https://matheuscomputacaopuc.atlassian.net/browse/PROJ-48)
  (back-end) e [PROJ-49](https://matheuscomputacaopuc.atlassian.net/browse/PROJ-49)
  (front-end).
- **Status**: Aprovada
- **Data**: 2026-11-21
- **Decisões gerais aplicadas**: D-004, D-012, D-013, D-020, D-021, D-030,
  D-032, D-033, D-034, D-040 e D-042.
- **Depende de**: spec 001 (conta e sessão), spec 003 (perfil de anunciante,
  contatos e foto) e spec 001-visualizar-feed-anuncios (card e navegação).

## Contexto

Ao clicar em um anúncio no feed, o comprador precisa abrir uma página dedicada
para conhecer a foto, ler a descrição completa, conferir as informações
do item, saber quem está vendendo e escolher uma forma de contato.

## Histórias de usuário

**H1. Como** comprador autenticado,
**quero** abrir a página detalhada de um anúncio,
**para que** eu veja todas as informações necessárias para decidir uma compra
ou contato.

**H2. Como** comprador autenticado,
**quero** acessar as formas de contato do anunciante,
**para que** eu possa iniciar uma conversa ou enviar uma mensagem pelo canal
que preferir.

## Critérios de aceitação

- [ ] CA1: Dado que clico em um card publicado no feed, quando a página
  detalhada carrega, então vejo título, categoria, estado de conservação,
  preço e descrição completa. Localização no campus não faz parte desta feature.
- [ ] CA2: Dado que o anúncio tem uma foto, quando a página carrega, então vejo
  essa foto em um estado visual adequado.
- [ ] CA3: Dado que o anúncio não tem foto, quando a página carrega, então
  vejo um estado visual adequado que não quebra o layout e oculta a galeria.
- [ ] CA4: Dado que o anúncio está publicado, quando a página carrega, então
  vejo o perfil resumido do anunciante com nome de exibição, vínculo e foto,
  quando houver.
- [ ] CA5: Dado um anunciante com contatos cadastrados, quando vejo o anúncio,
  então vejo os contatos permitidos para contato e consigo ativar WhatsApp,
  telefone, e-mail, site ou link conforme o tipo.
- [ ] CA6: Dado um WhatsApp informado por número, quando ativo o contato,
  então sou levado ao link de conversa correspondente.
- [ ] CA7: Dado um WhatsApp informado por link, quando ativo o contato, então
  sou levado ao link de conversa já cadastrado.
- [ ] CA8: Dado que não estou autenticado, quando tento abrir a página do
  anúncio, então não tenho acesso e sigo o comportamento de login definido pela
  plataforma.
- [ ] CA9: Dado um anúncio inexistente, quando tento abrir a página, então vejo
  uma mensagem informativa de anúncio não encontrado.
- [ ] CA10: Dado um anúncio excluído, quando tento abrir a página, então vejo
  uma mensagem informativa equivalente a anúncio indisponível.
- [ ] CA11: Dado um anúncio expirado, vendido ou não publicado, quando tento
  abrir a página, então vejo uma mensagem informativa adequada ao estado e não
  vejo botões que sugiram uma compra ou contato disponível.
- [ ] CA12: Dado que a página está carregando, quando espero a resposta da API,
  então vejo um estado de carregamento sem perder o usuário em uma tela vazia.
- [ ] CA13: Dado que a API falha ou não há conexão, quando tento abrir a
  página, então vejo uma mensagem de falha sem dados parciais enganosos.
- [ ] CA14: Dado que uso o celular, quando vejo a página, então a foto e as
  informações cabem sem rolagem horizontal.
- [ ] CA15: Dado que uso o teclado, quando navego pela página, então consigo
  acessar a foto e os links de contato com foco e rótulos acessíveis.
- [ ] CA16: A página segue o tema e os componentes existentes em
  `front/css/tema.css` e no guia de estilo.

## Regras de negócio

- RN1: A página só pode ser aberta por usuário autenticado com conta confirmada
  (D-004 e D-021).
- RN2: O anúncio exibido deve continuar publicado e disponível; excluído,
  vendido ou expirado não aparece como anúncio ativo.
- RN3: A publicação atual admite uma foto por anúncio. Quando houver foto,
  ela é exibida na página; quando não houver, a galeria é omitida e o layout
  mantém um estado visual vazio adequado.
- RN4: Os dados do anunciante exibidos são nome de exibição, vínculo e foto;
  os contatos vêm da lista de contatos do perfil de anunciante (D-013).
- RN5: Os dados sensíveis ou duplicados do perfil comum não precisam ser
  exibidos. O endereço institucional não substitui a escolha voluntária de
  contatos do anunciante.
- RN6: WhatsApp por número gera uma URL de conversa a partir do código do país
  e do número. WhatsApp por link usa o endereço cadastrado.
- RN7: A descrição completa não é limitada pelo resumo usado no feed.
- RN8: Mensagens de servidor são exibidas como texto; conteúdo de dados da API
  não é interpretado como HTML (D-031).
- RN9: A página usa o visual comum e o comportamento geral das telas
  (D-032 a D-034).

## Mensagens da página

- Sem sessão: `Faça login para ver os detalhes do anúncio.`
- Anúncio inexistente: `Anúncio não encontrado.`
- Anúncio vendido: `Este anúncio já foi vendido e não está mais disponível para contato.`
- Anúncio expirado: `Este anúncio expirou e não está mais disponível para contato.`
- Anúncio excluído: `Este anúncio foi excluído ou não está mais disponível.`
- Anúncio não publicado: `Este anúncio não está publicado.`
- Falha da API ou de conexão: `Não foi possível carregar o anúncio. Tente novamente.`
- Anúncio sem foto: `Este anúncio não possui foto.`

## Fora do escopo

- Publicar, editar ou excluir anúncios.
- Comprar diretamente, reservar ou negociar dentro da página.
- Chat interno.
- Moderação ou denúncia.
- Recuperação de senha.
- Geolocalização, mapa ou navegação externa além de links de contato já
  cadastrados.
- Alterar o perfil de anunciante ou seus contatos nesta tela.

## Dúvidas em aberto

- A apresentação visual final do estado sem foto e dos detalhes menores dos
  botões de contato pode seguir o tema e o guia de estilo.

