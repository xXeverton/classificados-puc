# Spec: Autenticação de membros PUC

- **ID**: 001
- **Status**: Rascunho
- **Data**: 2026-11-12

## História de usuário

**Como** pessoa com vínculo PUC,
**quero** entrar com meu e-mail institucional,
**para que** eu acesse a plataforma como membro identificado.

> Mudança de requisito (2026-11-12): o login passou de matrícula + senha para
> e-mail institucional + senha. Só são aceitos e-mails `@aluno.puc-rio.br` e
> `@puc-rio.br`.

## Critérios de aceitação

- [ ] CA1: Dado e-mail institucional e senha válidos, quando entro, então sou
  levado ao feed (recebo uma sessão autenticada).
- [ ] CA2: Dadas credenciais inválidas (e-mail não cadastrado ou senha
  errada), quando tento entrar, então vejo "E-mail ou senha inválidos".
- [ ] CA3: Dado que erro a senha 5 vezes seguidas, quando tento entrar de
  novo, então o login fica bloqueado por 10 minutos, mesmo com a senha certa.
- [ ] CA4: Dado que o bloqueio de 10 minutos terminou, quando entro com
  credenciais válidas, então consigo entrar.
- [ ] CA5: Dado um e-mail fora dos domínios `@aluno.puc-rio.br` e
  `@puc-rio.br`, quando tento entrar ou pedir um link, então vejo que preciso
  usar o e-mail institucional, e nenhuma tentativa é contada.
- [ ] CA6: Dado um e-mail institucional cadastrado, quando peço um link de
  acesso, então recebo por e-mail um link de uso único e validade curta que me
  autentica.
- [ ] CA7: Dado um link de acesso expirado ou já usado, quando o abro, então
  não sou autenticado.
- [ ] CA8: Dado que estou autenticado, quando acesso uma área restrita, então
  sou reconhecido; sem sessão válida, o acesso é negado.

## Regras de negócio

- RN1: O login usa e-mail institucional + senha.
- RN2: Só são aceitos e-mails dos domínios exatos `aluno.puc-rio.br` e
  `puc-rio.br`, sem diferenciar maiúsculas e ignorando espaços nas pontas.
  Subdomínios (ex.: `@ccc.puc-rio.br`) não são aceitos.
- RN3: Só entra quem tem vínculo de aluno ou funcionário, conforme o cadastro.
  O domínio do e-mail não define o vínculo. Terceirizados ficam fora por ora.
- RN4: Após 5 tentativas erradas consecutivas para o mesmo e-mail, o login
  desse e-mail fica bloqueado por 10 minutos. Um login bem-sucedido zera a
  contagem.
- RN5: A mensagem de erro de credenciais é sempre "E-mail ou senha
  inválidos", sem revelar se o e-mail está cadastrado.
- RN6: O pedido de link por e-mail tem sempre a mesma resposta para e-mails
  institucionais, cadastrados ou não.
- RN7: O link de acesso vale por 15 minutos e só pode ser usado uma vez.
- RN8: A senha nunca é armazenada em texto puro.

## Fora do escopo

- Tela de login e tela do feed (front-end).
- Cadastro de conta nova ("Criar conta") e recuperação de senha.
- Integração com a base oficial de matrículas da PUC.
- Logout com revogação no servidor (a sessão expira sozinha; o cliente
  descarta o token).

## Dúvidas em aberto

- A mensagem do CA2 mudou de "Matrícula ou senha inválidas" para "E-mail ou
  senha inválidos". O PO precisa confirmar o texto.
- O wireframe aprovado tem o campo "matrícula"; precisa ser trocado por
  "e-mail institucional".
- Com login por senha, o link mágico continua como acesso alternativo, vira
  recuperação de senha, ou sai do escopo?
- A validade de 15 minutos do link (RN7) e a duração da sessão precisam ser
  confirmadas com o PO.
- A coluna de senha e o registro persistente de tentativas ainda não existem
  no banco. Quem é responsável por essa mudança de modelagem?
