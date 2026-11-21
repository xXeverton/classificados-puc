# Spec: Perfil de anunciante

- **ID**: 003
- **Status**: Implementada (2026-11-21); aprovada em 2026-11-20, com contatos
  revistos no mesmo dia a pedido do time, antes de implementar a PROJ-28
- **Data**: 2026-11-20
- **Jira**: história [PROJ-4](https://matheuscomputacaopuc.atlassian.net/browse/PROJ-4);
  subtarefas [PROJ-25](https://matheuscomputacaopuc.atlassian.net/browse/PROJ-25)
  (modelagem do anunciante),
  [PROJ-28](https://matheuscomputacaopuc.atlassian.net/browse/PROJ-28)
  (salvar o perfil com foto),
  [PROJ-30](https://matheuscomputacaopuc.atlassian.net/browse/PROJ-30)
  (tela de perfil),
  [PROJ-27](https://matheuscomputacaopuc.atlassian.net/browse/PROJ-27)
  (formulário de edição) e
  [PROJ-29](https://matheuscomputacaopuc.atlassian.net/browse/PROJ-29)
  (redirecionamento de quem não é anunciante).
- **Depende de**: spec 001 (conta, sessão e vínculo) e spec 002 (telas de
  acesso, tema e comportamento geral das telas).
- **Decisões gerais aplicadas**: ver [`spec/decisoes.md`](../../decisoes.md),
  em especial D-004, D-005, D-010, D-012, D-013, D-020, D-025, D-032 e D-050.

## Contexto

Todo membro já tem um **perfil comum**, criado no cadastro (spec 001): nome,
e-mail institucional, nome de usuário, matrícula (se informada) e vínculo.

O **perfil de anunciante** é uma extensão opcional desse perfil comum. Nem
todo membro é anunciante: quem quiser anunciar escolhe, na tela do próprio
perfil, completar o perfil de anunciante, informando um nome de exibição, uma
foto (opcional) e **contatos**: as formas pelas quais os compradores podem
falar com a pessoa (WhatsApp, e-mail, telefone, site e outros links). Enquanto
não completar, a pessoa usa a plataforma normalmente, mas não pode publicar
anúncios.

A ordem de implementação acordada é: PROJ-25 (modelagem) → PROJ-28 (salvar
perfil) → PROJ-30 e PROJ-27 (telas) → PROJ-29 (redirecionamento).

## Histórias de usuário

**H1. Como** membro logado,
**quero** ver meu perfil e, se eu quiser, completar meu perfil de anunciante
com nome de exibição, foto (opcional) e as formas de contato que eu escolher,
**para que** eu possa anunciar e os compradores saibam quem sou e como falar
comigo.

**H2. Como** membro que ainda não é anunciante,
**quero** ser levado a completar meu perfil de anunciante quando tento
publicar um anúncio, e voltar para a publicação depois,
**para que** eu não perca o que estava fazendo.

## Critérios de aceitação

### Tela de perfil

- [x] CA1: Dado que estou logado, quando abro meu perfil, então vejo os dados
  do meu perfil comum (nome, e-mail institucional, nome de usuário, matrícula
  se informada e vínculo), sem poder alterá-los por ali.
- [x] CA2: Dado que ainda não sou anunciante, quando abro meu perfil, então
  vejo a opção de completar meu perfil de anunciante.
- [x] CA3: Dado que já sou anunciante, quando abro meu perfil, então vejo
  também meus dados de anunciante, com meus contatos, e a opção de editá-los.

### Completar e editar o perfil de anunciante

- [x] CA4: Dado que escolho completar meu perfil de anunciante, quando o
  formulário abre, então o nome de exibição vem preenchido com o nome da
  minha conta e a seção de contatos já traz um contato de e-mail com meu
  e-mail institucional; posso alterar ou remover tudo antes de salvar.
- [x] CA5: Dado que já sou anunciante, quando abro o formulário, então ele
  vem preenchido com meus dados de anunciante e meus contatos atuais, na
  ordem em que os salvei.
- [x] CA6: Dado um nome de exibição e ao menos um contato válido, quando
  salvo, então passo a ser anunciante e posso publicar anúncios.
- [x] CA7: Dado que não informo o nome de exibição (ou informo só espaços),
  quando salvo, então vejo que ele é obrigatório, e nada é salvo.
- [x] CA8: Dado que não informo nenhum contato, quando salvo, então vejo que
  é preciso ao menos um, e nada é salvo.
- [x] CA9: Dado que já sou anunciante, quando altero os dados e salvo, então
  os novos dados e a nova lista de contatos substituem os anteriores.
- [x] CA10: Dado que estou no formulário, então o vínculo aparece como
  somente leitura, vindo do cadastro.

### Contatos

- [x] CA11: Dado que adiciono um contato, então escolho o tipo entre WhatsApp,
  e-mail, telefone, site e link, e preencho o valor conforme o tipo.
- [x] CA12: Dado um contato de WhatsApp informado como **número**, quando
  seleciono o país numa lista de códigos de país e digito o número, então ele
  é aceito; o código do país é obrigatório e já vem selecionado como Brasil
  (+55).
- [x] CA13: Dado um contato de WhatsApp informado como **link**, quando colo
  um link de conversa do WhatsApp (por exemplo `https://wa.me/5521999999999`
  ou `https://wa.me/message/...`), então ele é aceito, mesmo sem número de
  telefone.
- [x] CA14: Dado um contato de **telefone**, quando seleciono o país (padrão
  Brasil, +55) e digito o número, então ele é aceito, seja fixo ou celular.
- [x] CA15: Dado um número (de WhatsApp ou de telefone) com letras ou com
  quantidade de dígitos fora do permitido, ou um link de WhatsApp que não é do
  WhatsApp, quando salvo, então vejo o motivo, e nada é salvo.
- [x] CA16: Dado um contato de **e-mail** válido de qualquer domínio (não só
  os da PUC-Rio), quando salvo, então ele é aceito; um e-mail em formato
  inválido gera um motivo, e nada é salvo.
- [x] CA17: Dado um contato de **site** ou de **link** com endereço
  `https://`, quando salvo, então ele é aceito; um endereço sem `https://`
  ou malformado gera um motivo, e nada é salvo.
- [x] CA18: Dado um contato de **link**, quando informo um rótulo (por
  exemplo "Instagram"), então o rótulo é salvo e mostrado junto do link; o
  rótulo é opcional e só existe para links.
- [x] CA19: Dado o formulário, quando adiciono vários contatos, inclusive
  mais de um do mesmo tipo (por exemplo, dois links), então todos são salvos,
  na ordem em que os organizei.
- [x] CA20: Dado um perfil com contatos, quando removo um contato e salvo,
  então ele deixa de existir; se removo todos, vale o CA8.
- [x] CA21: Dado que tento salvar mais de 10 contatos, então vejo o limite, e
  nada é salvo.
- [x] CA22: Dado dois contatos idênticos (mesmo tipo e mesmo valor), quando
  salvo, então vejo que há contato repetido, e nada é salvo.

### Foto

- [x] CA23: Dada uma foto JPG, PNG ou WEBP de até 2 MB, quando salvo, então o
  perfil de anunciante é salvo com essa foto.
- [x] CA24: Dada uma foto acima de 2 MB, em outro formato, ou um arquivo que
  não é de fato uma imagem nesses formatos, quando salvo, então vejo o motivo,
  e nada é salvo (os dados anteriores continuam como estavam).
- [x] CA25: Dado que não envio foto, quando salvo os demais dados válidos,
  então o perfil é salvo normalmente, sem foto.
- [x] CA26: Dado um perfil com foto, quando escolho remover a foto e salvo,
  então o perfil fica sem foto; se eu não enviar outra nem pedir para
  remover, a foto atual continua.

### Anunciar

- [x] CA27: Dado que estou logado e não sou anunciante, quando tento publicar
  um anúncio, então sou levado a completar meu perfil de anunciante.
- [x] CA28: Dado que fui levado ao formulário pelo CA27, quando salvo o
  perfil com sucesso, então volto automaticamente para a publicação do
  anúncio.
- [x] CA29: Dado que já sou anunciante, quando tento publicar um anúncio,
  então sigo direto para a publicação.

### Acesso

- [x] CA30: Dado que não estou logado, quando tento abrir o perfil, salvar o
  perfil de anunciante ou ver a foto de um perfil, então não tenho acesso e
  sou levado à tela de entrada.
- [x] CA31: Dado que estou logado, quando salvo o perfil de anunciante, então
  só o meu perfil é alterado; não é possível editar o perfil de outro membro.

## Regras de negócio

- RN1: Todo membro tem um **perfil comum**, que vem do cadastro (spec 001). O
  **perfil de anunciante** é uma extensão opcional dele, com **no máximo um**
  por conta. Os dados do perfil comum não são alterados por esta feature.
- RN2: Campos do perfil de anunciante: **nome de exibição** (obrigatório),
  **foto** (opcional) e **contatos** (lista com **ao menos um**).
- RN3: Só se salva um perfil de anunciante completo (RN2). **Ser anunciante
  é ter o perfil de anunciante salvo**, e essa é a condição para publicar
  anúncios. Não existe perfil de anunciante "pela metade".
- RN4: Cada **contato** tem um **tipo** e um valor. Os tipos são:
  - **WhatsApp**, de um destes jeitos:
    - *número*: código do país escolhido numa lista (obrigatório, padrão
      Brasil, +55) e o número, só com dígitos (espaços, parênteses e hífens
      são ignorados); código + número somam de **8 a 15 dígitos**. Os
      compradores veem um link que abre a conversa no WhatsApp;
    - *link*: link de conversa do WhatsApp (`https://wa.me/...` ou
      `https://api.whatsapp.com/...`), inclusive os que não mostram o número.
      Vale como contato e é mostrado como foi informado.
  - **Telefone**: código do país (lista, padrão +55) e número, com a mesma
    regra de dígitos do WhatsApp por número.
  - **E-mail**: qualquer domínio, desde que com formato de e-mail válido. Não
    é conferido se a caixa existe.
  - **Site**: endereço `https://`.
  - **Link**: endereço `https://` com **rótulo opcional** (por exemplo,
    "Instagram"). É para qualquer outra página que a pessoa queira mostrar.
- RN5: Um perfil tem **no máximo 10 contatos**, em qualquer combinação de
  tipos, inclusive vários do mesmo tipo. Dois contatos com o mesmo tipo e o
  mesmo valor não são aceitos.
- RN6: A foto é opcional e aceita **JPG, PNG ou WEBP** de no máximo **2 MB**.
  O formato é conferido pelo conteúdo do arquivo, não só pelo nome.
- RN7: O **vínculo** (aluno ou funcionário) vem do cadastro, aparece no perfil
  e não é editável aqui.
- RN8: Se algum dado enviado for inválido (incluindo a foto ou qualquer
  contato), **nada é salvo**, e o perfil continua como estava.
- RN9: O nome de exibição é guardado sem espaços nas pontas. O e-mail de
  contato é guardado em minúsculas. Endereços de site e de link são guardados
  como foram informados, sem espaços nas pontas. O nome de exibição não tem
  limite de tamanho próprio, como o nome da conta.
- RN10: Perfis e fotos só são vistos por quem está logado (D-004).
- RN11: As telas desta feature seguem o comportamento geral das telas da spec
  002 (CA23 a CA26 e CA28 de lá): botão indisponível durante o envio, aviso de
  falha de conexão sem perder o que foi preenchido, uso só pelo teclado com
  rótulos e erros junto aos campos, tela de celular sem rolagem horizontal e
  visual do tema comum.
- RN12: A **ordem dos contatos** é a que a pessoa definiu, e é a ordem em que
  eles são mostrados.
- RN13: Rótulos de link têm no máximo **40 caracteres** e endereços de site e
  de link, no máximo **2048 caracteres**. *(Confirmado pelo time em
  2026-11-20; ajustáveis em `politicas_perfil.py`.)*

## Fora do escopo

- Onde e como o perfil de anunciante aparece para os compradores (fica com a
  feature de anúncios; pendência P-001 de `spec/decisoes.md`).
- A publicação de anúncios em si. Aqui só entram a exigência de ser
  anunciante (CA27 a CA29) e uma tela provisória de "novo anúncio" para onde
  a pessoa é levada.
- Editar os dados do perfil comum (nome, e-mail, nome de usuário, matrícula,
  vínculo).
- Deixar de ser anunciante (excluir o perfil de anunciante).
- Recorte, redimensionamento ou compressão da foto.
- Conferir se os contatos pertencem de fato à pessoa, ou se o site e os links
  existem ou são seguros.
- Validação de formato de número específica de cada país.
- Outros tipos de contato além dos cinco da RN4 (por exemplo, redes sociais
  com campo próprio: a pessoa usa o tipo "link" com um rótulo).
- Moderação de fotos ou de dados do perfil.
- Wireframe: não há; as telas seguem o tema e o guia de estilo da spec 002
  (D-032).

## Decisões registradas

Todas confirmadas em 2026-11-20 e copiadas para `spec/decisoes.md` quando
valem para o projeto inteiro.

- Escopo: esta spec cobre a história PROJ-4 inteira; o `tasks.md` separa os
  blocos por subtarefa do Jira (D-050).
- Perfil comum × perfil de anunciante (RN1, RN3; D-010).
- **Contatos como lista** de tipos WhatsApp, e-mail, telefone, site e link,
  com WhatsApp por número ou por link (RN4, RN5; D-013). Isso substitui a
  decisão anterior de ter só WhatsApp e e-mail (D-011).
- Telefone com a mesma regra de país e dígitos do WhatsApp por número (RN4).
- Site e links só com `https://`; link com rótulo opcional (RN4).
- Limite de 10 contatos no total, sem contatos repetidos (RN5).
- Rótulo de link com até 40 caracteres e endereços com até 2048 (RN13).
- Foto: JPG, PNG e WEBP até 2 MB (RN6; D-012).
- O formulário parte do perfil comum: nome e e-mail da conta vêm
  preenchidos (CA4).
- Depois de completar o perfil vindo da tentativa de anunciar, a pessoa volta
  para a publicação (CA28).
- Login obrigatório também para ver fotos de perfil (RN10; D-004).
- Sem wireframe: seguir o tema e o guia de estilo da spec 002 (D-032).
- Rotas no padrão das já existentes (D-020).

## Dúvidas em aberto

- Nenhuma que bloqueie esta feature. A visibilidade do perfil para os
  compradores fica com a feature de anúncios (P-001).
- Os limites da RN13 (40 e 2048 caracteres) e a recusa de contatos repetidos
  (RN5) foram confirmados pelo time em 2026-11-20, como implementados.
