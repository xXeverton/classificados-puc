# Tarefas: Telas de entrada, cadastro e confirmação de e-mail

Referências: `spec.md` e `plan.md` desta pasta. Jira: PROJ-21.
Marque `[x]` ao concluir. Escreva os testes antes da implementação.
Rode `make front-test` ao fim de cada bloco.

## 0. Preparação

- [x] T0: Fechar as dúvidas da `spec.md` sobre confirmar senha,
  mostrar/ocultar senha e textos das mensagens (respondidas em 2026-11-20).
  Spec confirmada em 2026-11-20, com teste no navegador.
- [x] T0a: Criar o tema comum `front/css/tema.css` (tokens e componentes) e a
  demonstração `front/guia-de-estilo/index.html`. (CA28)
- [x] T1: Criar o resto da estrutura de `front/` (pastas, `package.json` com
  `"type": "module"`, `config.js`) e os alvos `front` e `front-test` no
  `Makefile`.
- [x] T2: Conferir com o `http.server` que
  `http://localhost:5173/confirmar-email?token=abc` chega a
  `/confirmar-email/?token=abc` com a query mantida. Se não chegar, registrar
  no `plan.md` e documentar o `CONFIRMACAO_URL_BASE` com a barra final.

## 1. Domínio (`front/js/dominio/`)

- [x] T3: Testes de `validarLogin` e `validarCadastro` em
  `tests/regras_cadastro.test.js`: obrigatórios, domínio (incluindo
  maiúsculas e espaços), senha com 7 e com 8 caracteres, `@` no nome de
  usuário, matrícula vazia aceita, confirmação diferente da senha recusada.
  (CA6, CA8–CA11a)
- [x] T4: Implementar `regras_cadastro.js` e `mensagens.js` até T3 passar.

## 2. Adaptadores (`front/js/adaptadores/`)

- [x] T5: Criar `tests/fakes.js` (fetch falso que registra as chamadas e
  devolve respostas programadas; armazenamento em memória).
- [x] T6: Testes e implementação de `cliente_http.js`: URL com
  `API_BASE_URL`, corpo JSON, header Bearer quando houver token, retorno
  `{status, corpo}`, `ErroDeConexao` quando o `fetch` rejeita. (CA24)
- [x] T7: Testes e implementação de `armazenamento_sessao.js`: salvar, ler,
  apagar; sessão vencida tratada como ausente e apagada. (CA21)
- [x] T8: Implementar `auth_api.js` com uma função por rota `/auth/*`, usando
  o `cliente_http`.

## 3. Fluxos (`front/js/fluxos/`)

- [x] T9: Testes e implementação de `entrar.js`: validação local sem chamar a
  API; 200 salva a sessão; 401, 403 `email_nao_confirmado`, 429, 400 e falha
  de conexão viram estados de tela distintos. (CA2–CA6, CA24)
- [x] T10: Testes e implementação de `cadastrar.js`: validação local sem
  chamar a API; 201 vira o estado "verifique seu e-mail" com o endereço; 400
  e 409 trazem a mensagem do servidor; falha de conexão. (CA8–CA13, CA24)
- [x] T11: Testes e implementação de `reenviar_confirmacao.js`: 202 devolve a
  mensagem genérica do servidor; e-mail vazio ou fora do domínio não chama a
  API. (CA4, CA12, CA16)
- [x] T12: Testes e implementação de `confirmar_email.js`: sem token não chama
  a API; 200, 410 e 400 viram sucesso, expirado e inválido. (CA15–CA18)
- [x] T13: Testes e implementação de `sessao_atual.js`: sem sessão salva pede
  ida a `/entrar/`; 200 devolve o usuário; 401 apaga a sessão; sair apaga a
  sessão com 204 e com 401. (CA19–CA22)

## 4. Páginas (`front/*/index.html` e `front/js/paginas/`)

- [x] T14: `paginas/comum.js`: mostrar e limpar erro por campo
  (`aria-describedby`, `aria-invalid`, foco no primeiro erro), região
  `aria-live` para mensagens gerais, estado de carregando no botão, botão
  mostrar/ocultar senha. Só `textContent`, sem `innerHTML`. Usar as classes
  do `tema.css`. (CA23, CA25, CA27, RN7)
- [x] T15: Tela de entrada (`entrar/`), com o reenvio quando a conta está
  pendente, e o redirecionamento quando já há sessão. (CA1–CA6, CA19)
- [x] T16: Tela de cadastro (`cadastro/`), com a tela de "verifique seu
  e-mail" e o reenvio, e o redirecionamento quando já há sessão. (CA7–CA13,
  CA19)
- [x] T17: Página de confirmação (`confirmar-email/`): botão de confirmar,
  estados de sucesso, expirado (com formulário de reenvio), inválido e sem
  token. (CA14–CA18)
- [x] T18: Página inicial logada provisória (`inicio/`) com nome e botão de
  sair, e `index.html` da raiz redirecionando. (CA20–CA22)

## 5. Documentação

- [x] T19: Atualizar `ARQUITETURA.md` (front em `front/`, estrutura, regra de
  dependências, linha "UI" e diagrama) e a seção 12 do `ROTEIRO.md`.
- [x] T20: Atualizar o `README.md`: `make front`, `CORS_ORIGINS=http://localhost:5173`
  em dev, `make front-test`, Node 18 ou mais novo para os testes, como usar o
  `tema.css` e o guia de estilo, e que o `CONFIRMACAO_URL_BASE` precisa apontar
  para o front publicado quando o backend for usado por outras pessoas.

## 6. Validação

- [x] T21: `make front-test` passando.
- [x] T22: `make check` (pytest e flake8 do backend) continua passando.
- [x] T23: Roteiro manual com o backend real (`EMAIL_BACKEND=log`,
  `CORS_ORIGINS=http://localhost:5173`): cadastro → link do log → confirmação
  por clique → entrada por e-mail, nome de usuário e matrícula → sair; casos
  de erro de cada tela; link expirado e já usado; 5 senhas erradas; backend
  desligado; navegação só por teclado; largura de celular (360 px).
- [x] T24: Conferir `grep -r innerHTML front/js` sem ocorrências. (RN7)
- [x] T25: Conferir o mapa critério → teste do `plan.md`, marcar os CAs na
  `spec.md` e mudar o status para `Implementada`.
