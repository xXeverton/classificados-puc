# Spec: Cadastro, login e verificação de e-mail institucional

- **ID**: 001
- **Status**: Implementada (pendente apenas o teste manual de SMTP, T34)
- **Data**: 2026-11-20
- **Jira**: história [PROJ-1](https://matheuscomputacaopuc.atlassian.net/browse/PROJ-1);
  subtarefa [PROJ-23](https://matheuscomputacaopuc.atlassian.net/browse/PROJ-23),
  que absorveu a [PROJ-24](https://matheuscomputacaopuc.atlassian.net/browse/PROJ-24)
  (rotas de autenticação e sessão).

## Contexto

A PROJ-1 previa login por matrícula e senha, com o e-mail institucional como
plano B. O grupo adotou o plano B: no MVP, a plataforma é restrita a pessoas
com e-mail institucional da PUC-Rio, que entram com e-mail e senha.

### Decisão de produto (MVP)

O e-mail institucional é a regra de negócio que define a comunidade e
substitui, no MVP, a moderação de conteúdo como mecanismo de confiança. Não há
acesso de pessoas externas, nem papéis ou permissões baseados em verificação
manual.

Justificativa:

1. Alinhada ao escopo do produto: anúncios de pessoas vinculadas à PUC-Rio.
2. Reduz o risco de golpes e spam sem depender de moderação.
3. Evita a complexidade de papéis, permissões e fluxo de aprovação manual.
4. Evita o gargalo operacional de verificar cadastros manualmente.

Para que o domínio do e-mail sirva como garantia, é preciso provar que a pessoa
controla aquela caixa. Por isso o cadastro só é concluído depois da
confirmação automática por um link enviado ao e-mail institucional.

## Histórias de usuário

**H1. Como** pessoa com e-mail institucional da PUC-Rio,
**quero** me cadastrar informando nome, e-mail, nome de usuário, vínculo,
senha e, se eu quiser, minha matrícula,
**para que** eu tenha acesso à plataforma.

**H2. Como** pessoa recém-cadastrada,
**quero** confirmar meu e-mail por um link enviado à minha caixa,
**para que** a plataforma saiba que o endereço é realmente meu.

**H3. Como** membro com cadastro confirmado,
**quero** entrar informando meu e-mail, meu nome de usuário ou minha
matrícula, e a senha,
**para que** eu use a plataforma identificado.

## Critérios de aceitação

### Cadastro

- [x] CA1: Dados nome, vínculo, um e-mail `@puc-rio.br` ou
  `@aluno.puc-rio.br` ainda não cadastrado, um nome de usuário disponível e
  uma senha válida, quando me cadastro, então a conta é criada como
  **pendente de confirmação** e recebo um e-mail com um link de confirmação.
- [x] CA2: Dado um e-mail de qualquer outro domínio, quando tento me
  cadastrar, então vejo que apenas e-mails institucionais da PUC-Rio são
  aceitos, e a conta não é criada.
- [x] CA3: Dado um e-mail que já pertence a uma conta confirmada, quando tento
  me cadastrar, então vejo que o e-mail já está em uso.
- [x] CA4: Dada uma senha com menos de 8 caracteres, quando tento me
  cadastrar, então vejo o motivo e a conta não é criada.
- [x] CA5: Dado que não informo o nome ou o vínculo, ou informo um vínculo
  diferente de aluno ou funcionário, quando tento me cadastrar, então vejo o
  motivo e a conta não é criada.
- [x] CA6: Dado um nome de usuário que já pertence a outra conta, quando tento
  me cadastrar com ele, então vejo que o nome de usuário já está em uso, e a
  conta não é criada.
- [x] CA7: Dado um nome de usuário com `@`, quando tento me cadastrar, então
  vejo o motivo e a conta não é criada.
- [x] CA8: Dado que não informo a matrícula, quando me cadastro com os demais
  dados válidos, então a conta é criada normalmente.
- [x] CA9: Dada uma matrícula que já pertence a outra conta, quando tento me
  cadastrar com ela, então vejo que a matrícula já está em uso, e a conta não
  é criada.
- [x] CA10: Dado um nome de usuário igual à matrícula de outra conta (ou uma
  matrícula igual ao nome de usuário de outra conta), quando tento me
  cadastrar, então vejo que o identificador já está em uso, e a conta não é
  criada.
- [x] CA11: Dado um e-mail que já pertence a uma conta **pendente de
  confirmação**, quando me cadastro de novo com ele, então o cadastro pendente
  é substituído pelos novos dados, recebo um novo link, e os links anteriores
  deixam de valer.

### Confirmação de e-mail

- [x] CA12: Dado um link de confirmação válido, quando o abro em até 15
  minutos, então minha conta passa a ser **confirmada** e posso entrar.
- [x] CA13: Dado um link com mais de 15 minutos, quando o abro, então vejo que
  ele expirou e posso pedir um novo.
- [x] CA14: Dado um link já usado, quando o abro de novo, então ele é recusado.
- [x] CA15: Dada uma conta pendente de confirmação, quando peço para reenviar o
  link, então recebo um novo, e os anteriores deixam de valer.

### Login e saída

- [x] CA16: Dados e-mail e senha corretos de uma conta confirmada, quando entro,
  então sou levado ao feed, já identificado.
- [x] CA17: Dados nome de usuário e senha corretos de uma conta confirmada,
  quando entro, então sou levado ao feed, já identificado.
- [x] CA18: Dados matrícula e senha corretos de uma conta confirmada que
  informou matrícula, quando entro, então sou levado ao feed, já identificado.
- [x] CA19: Dados identificador (e-mail, nome de usuário ou matrícula) e
  senha corretos de uma conta
  pendente de confirmação, quando tento entrar, então vejo que preciso confirmar meu
  e-mail, com a opção de reenviar o link, e não entro.
- [x] CA20: Dado um identificador que não corresponde a nenhuma conta, ou uma
  senha incorreta, quando tento entrar, então vejo "Credenciais inválidas",
  sem indicar qual dado está errado.
- [x] CA21: Dado que errei a senha 5 vezes seguidas, quando tento entrar de
  novo, então o login dessa conta fica bloqueado por 10 minutos, seja qual
  for o identificador usado (e-mail, nome de usuário ou matrícula).
- [x] CA22: Dado que estou logado, quando saio, então perco o acesso até entrar
  de novo.

### Acesso à plataforma

- [x] CA23: Dado que não estou logado, quando tento acessar qualquer conteúdo
  da plataforma (feed, anúncios, eventos), então sou levado à tela de entrada.

## Regras de negócio

- RN1: Só são aceitos e-mails dos domínios `@puc-rio.br` e
  `@aluno.puc-rio.br` (validação já existente, entregue na PROJ-22). O e-mail
  é comparado sem diferenciar maiúsculas de minúsculas, e cada e-mail
  corresponde a no máximo uma conta.
- RN2: Uma conta só dá acesso à plataforma depois de confirmada pelo link
  enviado ao e-mail. Não há aprovação manual.
- RN3: O link de confirmação vale por **15 minutos** e pode ser usado **uma
  única vez**. Pedir um novo link invalida os anteriores.
- RN4: A senha deve ter **no mínimo 8 caracteres** e nunca é armazenada em
  texto puro.
- RN5: Após **5 tentativas de login erradas seguidas**, a conta fica bloqueada
  para login por **10 minutos**. Um login correto zera a contagem.
- RN6: Todo conteúdo da plataforma exige estar logado com conta confirmada.
  Não há acesso anônimo nem diferença de permissões entre membros no MVP.
- RN7: No cadastro, a pessoa informa nome, e-mail, nome de usuário, vínculo
  e senha; a matrícula é **opcional**. O vínculo é escolhido entre **aluno** e
  **funcionário**.
- RN8: O **e-mail é o identificador principal da conta**. Nome de usuário e
  matrícula são identificadores alternativos que pertencem à conta daquele
  e-mail.
- RN9: Um novo cadastro com o e-mail de uma conta ainda pendente de
  confirmação **substitui** o cadastro pendente (novos dados, nova senha e novo
  link). Assim, um cadastro feito por outra pessoa com o seu e-mail não
  bloqueia o endereço.
- RN10: O login usa **um único campo de identificação**, que aceita e-mail,
  nome de usuário ou matrícula, e um campo de senha.
- RN11: O nome de usuário é obrigatório e não pode conter `@`. A matrícula,
  quando informada, é guardada como foi digitada; a plataforma não confere se
  ela pertence de fato a quem a informou.
- RN12: Nome de usuário e matrícula são únicos **entre si**: nenhum valor pode
  ser, ao mesmo tempo, o nome de usuário de uma conta e a matrícula de outra.
  Assim, cada identificador digitado no login aponta para no máximo uma conta.
  Comparações não diferenciam maiúsculas de minúsculas.
- RN13: Um cadastro pendente reserva o nome de usuário e a matrícula só até o
  último link de confirmação expirar. Depois disso, eles ficam livres para
  outro cadastro, para que ninguém reserve a matrícula de outra pessoa sem
  confirmar o próprio e-mail.
- RN14: O bloqueio da RN5 vale para a conta, qualquer que seja o
  identificador usado no login.

## Fora do escopo

- Acesso de pessoas sem e-mail institucional da PUC-Rio.
- Papéis, permissões diferenciadas e aprovação manual de cadastros.
- Moderação de conteúdo.
- Recuperação de senha ("esqueci minha senha").
- Conferência da matrícula em sistemas acadêmicos da PUC-Rio.
- Alteração do nome de usuário ou da matrícula depois do cadastro.
- Outros vínculos além de aluno e funcionário (ex.: terceirizados).
- Login social (Google, Microsoft etc.).
- Alteração de e-mail de uma conta existente.
- Telas de front-end (tratadas na PROJ-21), exceto pelo comportamento descrito
  nos critérios.

## Decisões registradas

- Envio de e-mail (técnica, detalhada no `plan.md`): em desenvolvimento e
  testes o conteúdo do e-mail aparece no log da aplicação; nos demais
  ambientes é enviado por SMTP configurado por variáveis de ambiente. Trocar
  de provedor depois é só configuração.
- Matrícula passa a ser opcional (RN7). Hoje a entidade `Usuario` e a
  tabela `usuarios` exigem `matricula`; o `plan.md` deve tratar essa mudança
  de modelo e o novo campo de nome de usuário.
- O e-mail é o identificador principal da conta (RN8). Se isso vira a chave
  primária da tabela ou se o `id` numérico continua como chave técnica, com o
  e-mail único, é decisão do `plan.md`.
- Vínculo é informado no cadastro, entre aluno e funcionário (RN7).
- Login por um único campo que aceita e-mail, nome de usuário ou matrícula
  (RN10).
- Nome de usuário: a única restrição de formato é não conter `@` (RN11).
- Identificadores de cadastro pendente ficam livres quando o último link
  expira (RN13).
- Senha com no mínimo 8 caracteres (RN4).
- Cadastro pendente é substituído por um novo cadastro com o mesmo e-mail
  (RN9).
- Jira: a PROJ-24 foi incorporada à PROJ-23, e a PROJ-1 foi atualizada para o
  login por e-mail institucional.

## Dúvidas em aberto

- Nenhuma no momento.
