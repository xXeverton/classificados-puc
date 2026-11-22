# Spec: Detalhar anúncio

- **ID**: 004
- **Jira**: história [PROJ-17](https://matheuscomputacaopuc.atlassian.net/browse/PROJ-17);
  subtarefas [PROJ-48](https://matheuscomputacaopuc.atlassian.net/browse/PROJ-48)
  (back-end) e [PROJ-49](https://matheuscomputacaopuc.atlassian.net/browse/PROJ-49)
  (front-end).
- **Status**: Rascunho
- **Data**: 2026-11-21
- **Depende de**: spec 001 (conta e sessão), spec 003 (perfil de anunciante,
  contatos e foto) e spec 001-visualizar-feed-anuncios (card e navegação).

## Contexto

Ao clicar em um anúncio no feed, o comprador precisa abrir uma página dedicada
para conhecer todas as fotos, ler a descrição completa, conferir as informações
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
  preço, descrição completa e localização no campus.
- [ ] CA2: Dado que o anúncio tem fotos, quando a página carrega, então vejo
  uma galeria ou carrossel com todas as fotos e consigo navegar entre elas.
- [ ] CA3: Dado que o anúncio não tem fotos, quando a página carrega, então
  vejo um estado visual adequado que não quebra o layout.
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
- [ ] CA14: Dado que uso o celular, quando vejo a página, então a galeria e as
  informações cabem sem rolagem horizontal.
- [ ] CA15: Dado que uso o teclado, quando navego pela página, então consigo
  operar a galeria e os links de contato com foco e rótulos acessíveis.
- [ ] CA16: A página segue o tema e os componentes existentes em
  `front/css/tema.css` e no guia de estilo.

## Regras de negócio

- RN1: A página só pode ser aberta por usuário autenticado com conta confirmada
  (D-004 e D-021).
- RN2: O anúncio exibido deve continuar publicado e disponível; excluído,
  vendido ou expirado não aparece como anúncio ativo.
- RN3: A galeria mostra todas as fotos anexadas ao anúncio. Uma foto ausente
  usa o fallback aprovado nesta feature.
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

- Como a localização no campus é cadastrada: campo livre ou lista fechada,
  em qual feature e em qual campo da publicação.
- Qual campo representa o estado de conservação na publicação e quais valores
  são aceitos.
- Qual fallback usar quando o anúncio não tem fotos: imagem padrão ou galeria
  completamente omitida.
- O texto exato das mensagens para anúncio vendido, expirado, excluído,
  inexistente ou não publicado.
- Como múltiplas fotos são armazenadas e quais formatos e limites serão usados.
- Qual comportamento visual exato do carrossel e dos botões de contato; o
  wireframe desta spec é o layout de referência, mas não aprova detalhes finais.

