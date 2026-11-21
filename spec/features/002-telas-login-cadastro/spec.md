# Spec: Telas de entrada, cadastro e confirmação de e-mail

- **ID**: 002
- **Status**: Implementada
- **Data**: 2026-11-20
- **Jira**: história [PROJ-1](https://matheuscomputacaopuc.atlassian.net/browse/PROJ-1);
  subtarefa [PROJ-21](https://matheuscomputacaopuc.atlassian.net/browse/PROJ-21).
- **Depende de**: spec 001 (`spec/features/001-cadastro-login-verificacao-email/`),
  já implementada. As regras de negócio de cadastro, confirmação, login e
  bloqueio valem como estão lá; esta spec descreve só o que a pessoa vê e faz
  nas telas.

## Contexto

A spec 001 entregou o comportamento de cadastro, confirmação por link e login
com e-mail institucional, mas deixou as telas para a PROJ-21. Sem elas, nenhuma
pessoa consegue usar a plataforma. Esta feature cria as telas dedicadas de
entrada, cadastro e confirmação de e-mail, mais um destino mínimo depois do
login (o feed real é outra feature).

## Histórias de usuário

**H1. Como** pessoa com e-mail institucional da PUC-Rio,
**quero** uma tela de cadastro que me diga com clareza o que preencher e o que
está errado,
**para que** eu crie minha conta sem tentativa e erro.

**H2. Como** pessoa recém-cadastrada,
**quero** ver que preciso confirmar meu e-mail e conseguir confirmar pelo link
recebido,
**para que** eu saiba exatamente o próximo passo.

**H3. Como** membro com cadastro confirmado,
**quero** uma tela de entrada com um único campo de identificação e a senha,
**para que** eu entre rápido com o identificador que eu lembrar.

## Critérios de aceitação

### Tela de entrada

- [x] CA1: Dado que abro a tela de entrada, então vejo um campo de
  identificação (que aceita e-mail, nome de usuário ou matrícula), um campo de
  senha, o botão de entrar e um caminho para a tela de cadastro.
- [x] CA2: Dados identificador e senha corretos de uma conta confirmada, quando
  entro, então sou levado à página inicial logada, já identificado pelo nome.
- [x] CA3: Dados um identificador inexistente ou uma senha errada, quando tento
  entrar, então vejo "Credenciais inválidas", sem indicar qual dado está
  errado; o identificador continua preenchido e a senha é apagada.
- [x] CA4: Dada uma conta pendente de confirmação, quando tento entrar com a
  senha certa, então vejo que preciso confirmar meu e-mail e uma opção para
  reenviar o link. Ao reenviar, vejo uma mensagem genérica de que, se houver
  cadastro pendente, um novo link foi enviado.
- [x] CA5: Dada uma conta bloqueada por excesso de tentativas, quando tento
  entrar, então vejo que o acesso está bloqueado temporariamente e que posso
  tentar de novo em alguns minutos.
- [x] CA6: Dado que deixo o identificador ou a senha vazios, quando tento
  entrar, então vejo qual campo falta e nada é enviado.

### Tela de cadastro

- [x] CA7: Dado que abro a tela de cadastro, então vejo os campos nome,
  e-mail institucional, nome de usuário, vínculo (aluno ou funcionário),
  matrícula (marcada como opcional), senha e confirmação da senha, o botão de
  cadastrar e um caminho para a tela de entrada.
- [x] CA8: Dado um e-mail que não termina em `@puc-rio.br` ou
  `@aluno.puc-rio.br`, quando tento cadastrar, então vejo, junto ao campo, que
  só e-mails institucionais da PUC-Rio são aceitos, e nada é enviado.
- [x] CA9: Dada uma senha com menos de 8 caracteres, quando tento cadastrar,
  então vejo, junto ao campo, o tamanho mínimo, e nada é enviado.
- [x] CA10: Dado um nome de usuário com `@`, quando tento cadastrar, então vejo,
  junto ao campo, que ele não pode conter `@`, e nada é enviado.
- [x] CA11: Dado que deixo vazio um campo obrigatório (nome, e-mail, nome de
  usuário, vínculo, senha ou confirmação da senha), quando tento cadastrar,
  então vejo, junto a cada campo, que ele é obrigatório, e nada é enviado.
- [x] CA11a: Dado que a confirmação da senha é diferente da senha, quando
  tento cadastrar, então vejo, junto à confirmação, que as senhas não
  conferem, e nada é enviado.
- [x] CA12: Dados todos os campos válidos, quando cadastro, então vejo uma tela
  avisando que enviamos um link de confirmação para o e-mail informado (o
  endereço aparece na tela), que o link vale por 15 minutos, e uma opção de
  reenviar o link.
- [x] CA13: Dado um e-mail, nome de usuário ou matrícula que já está em uso,
  quando tento cadastrar, então vejo a mensagem que o servidor devolve, e os
  dados que preenchi continuam na tela, exceto a senha e a confirmação.

### Página de confirmação de e-mail

- [x] CA14: Dado que abro o link de confirmação recebido por e-mail, então vejo
  uma página com o botão "Confirmar meu e-mail"; a confirmação só acontece
  quando clico nele.
- [x] CA15: Dado um link válido, quando clico em confirmar, então vejo que meu
  e-mail foi confirmado e um caminho para a tela de entrada.
- [x] CA16: Dado um link expirado, quando clico em confirmar, então vejo que o
  link expirou e posso informar meu e-mail para receber um novo.
- [x] CA17: Dado um link já usado ou inválido, quando clico em confirmar, então
  vejo que o link não é válido, com caminhos para entrar ou para me cadastrar
  de novo.
- [x] CA18: Dado que abro a página de confirmação sem o código do link, então
  vejo que o link está incompleto, sem o botão de confirmar.

### Sessão e navegação

- [x] CA19: Dado que já estou logado, quando abro a tela de entrada ou de
  cadastro, então sou levado à página inicial logada.
- [x] CA20: Dado que não estou logado, quando abro a página inicial logada,
  então sou levado à tela de entrada.
- [x] CA21: Dado que minha sessão expirou ou foi encerrada, quando abro a
  página inicial logada, então sou levado à tela de entrada com o aviso de que
  preciso entrar de novo.
- [x] CA22: Dado que estou logado, quando clico em sair, então volto à tela de
  entrada e perco o acesso até entrar de novo.

### Comportamento geral das telas

- [x] CA23: Dado que enviei um formulário, enquanto espero a resposta, então o
  botão fica indisponível e vejo que a ação está em andamento, sem envio
  duplicado.
- [x] CA24: Dado que o servidor está fora do ar ou sem conexão, quando envio um
  formulário, então vejo uma mensagem de falha de conexão, e o que preenchi
  continua na tela.
- [x] CA25: Dado que uso só o teclado, então consigo preencher e enviar todos
  os formulários (Enter envia), cada campo tem um rótulo visível, e as
  mensagens de erro ficam associadas ao campo e são anunciadas por leitores de
  tela.
- [x] CA26: Dado que abro as telas no celular, então elas cabem na largura da
  tela, sem rolagem horizontal.
- [x] CA27: Dado um campo de senha (entrada, cadastro e confirmação), quando
  clico em "Mostrar", então vejo a senha digitada e o botão passa a "Ocultar";
  clicando de novo, ela volta a ficar oculta.
- [x] CA28: Dado que abro qualquer tela, então ela segue o visual comum do
  projeto (`front/css/tema.css`): fonte, cores, botões em pílula e, nas telas
  de entrada e cadastro, a marca à esquerda, um divisor e o formulário à
  direita, como no login do Ambiente de Aprendizagem On-line da PUC-Rio.

## Regras de negócio

- RN1: As regras da spec 001 (domínios aceitos, senha mínima de 8 caracteres,
  nome de usuário sem `@`, matrícula opcional, vínculo entre aluno e
  funcionário, link de 15 minutos e uso único, bloqueio de 10 minutos após 5
  falhas) continuam valendo e o servidor é a fonte da verdade.
- RN2: As telas conferem antes de enviar só as regras que não dependem de
  dados de outras contas: campos obrigatórios, domínio do e-mail, tamanho
  mínimo da senha e `@` no nome de usuário. Disponibilidade de e-mail, nome de
  usuário e matrícula só o servidor responde.
- RN3: Mensagens de falha de login nunca indicam qual dado está errado (CA20
  da spec 001).
- RN4: A resposta ao reenvio do link é sempre genérica, sem revelar se o
  e-mail tem cadastro (mesma mensagem do servidor).
- RN5: A confirmação de e-mail exige um clique na página. Abrir o link sozinho
  não confirma, porque filtros de e-mail da universidade abrem links
  automaticamente e consumiriam o link de uso único.
- RN6: A senha digitada nunca é mantida na tela depois de uma falha nem
  guardada no navegador.
- RN7: Dados digitados pela pessoa ou vindos do servidor são exibidos como
  texto, nunca interpretados como conteúdo da página.

## Fora do escopo

- O feed e qualquer conteúdo real da plataforma. Depois do login, a pessoa vai
  para uma página inicial mínima que mostra o nome dela e o botão de sair, até
  a feature do feed existir.
- Recuperação de senha ("esqueci minha senha").
- Edição de perfil, troca de e-mail, nome de usuário ou matrícula.
- Uso do logotipo oficial da PUC-Rio. A marca é um texto ("PUC |
  Classificados"); trocar por um logo depende de autorização.
- Mudanças nas regras ou nas rotas do backend da spec 001.
- Outros idiomas além do português.
- Publicar o front e a API em um endereço acessível por outras pessoas
  (deploy). Ver "Dúvidas em aberto" sobre o link de confirmação.

## Decisões registradas

- Telas dedicadas (não modais): entrada, cadastro, confirmação de e-mail e a
  página inicial logada provisória. Confirmado em 2026-11-20.
- Tecnologia: HTML, CSS e JavaScript puros, sem framework. Confirmado em
  2026-11-20; detalhes no `plan.md`.
- O código do front-end fica neste repositório, na pasta `front/`, fora de
  `server/`. Confirmado em 2026-11-20. Isso muda a nota do `ARQUITETURA.md`
  que dizia que o front era externo.
- Confirmação por clique (RN5), seguindo a decisão do `plan.md` da spec 001 de
  não ter rota que confirme ao abrir o link.
- Confirmação de senha no cadastro (CA11a). É conferida só na tela; o
  servidor continua recebendo uma senha. Confirmado em 2026-11-20.
- Botão de mostrar/ocultar senha em todos os campos de senha (CA27).
  Confirmado em 2026-11-20.
- Mensagens: erros de cadastro mostram o texto que o servidor devolve; as
  validações locais, a falha de conexão e o bloqueio usam textos próprios das
  telas. Confirmado em 2026-11-20.
- Visual (CA28): inspirado no login do Ambiente de Aprendizagem On-line da
  PUC-Rio (fonte Rethink Sans, fundo `#f8f8f8`, azul `#213f7c`, botões em
  pílula, layout marca | divisor | formulário), com componentes de
  classificado (cartão de anúncio, preço, etiquetas). Fica em
  `front/css/tema.css`, compartilhado por todas as telas do grupo, com
  demonstração em `front/guia-de-estilo/`. Pedido em 2026-11-20.

## Dúvidas em aberto

- Link de confirmação fora da máquina local: o endereço do link vem do
  `CONFIRMACAO_URL_BASE` do backend que enviou o e-mail. Em desenvolvimento
  ele é `http://localhost:5173/...`, que funciona só para quem roda front e
  backend na própria máquina. Para outras pessoas testarem com o mesmo
  backend, o front precisa estar publicado em um endereço público e o
  `CONFIRMACAO_URL_BASE` apontar para ele. Onde publicar (e quando) ainda não
  está decidido; fica fora desta feature.
