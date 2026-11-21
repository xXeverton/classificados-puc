# Plano técnico: Telas de entrada, cadastro e confirmação de e-mail

Referência: `spec.md` desta pasta. Contrato da API: `plan.md` da spec 001
(seção "Interface web") e `server/api/controllers/auth_controller.py`.

## Decisões técnicas

| Tema | Decisão | Motivo |
|---|---|---|
| Local | Pasta `front/` na raiz do repositório, irmã de `server/`. | Confirmado com o time. O front é outro adaptador de entrada: só conversa com a API por HTTP e não importa nada de `server/`. |
| Tecnologia | HTML, CSS e JavaScript puros, com módulos ES (`<script type="module">`). Sem framework, sem bundler, sem dependências de npm. | Confirmado com o time. Os navegadores atuais suportam módulos ES nativamente, e não há etapa de build. |
| Servidor local | `python -m http.server 5173 --directory front`. | Já temos Python no projeto. A porta 5173 é a do `CONFIRMACAO_URL_BASE` padrão (`http://localhost:5173/confirmar-email`), então o link do e-mail funciona sem mudar a configuração. |
| Rotas das telas | Uma pasta por tela com `index.html`: `/entrar/`, `/cadastro/`, `/confirmar-email/`, `/inicio/`. `/` redireciona para `/inicio/` ou `/entrar/`. | Com o `http.server`, `/confirmar-email?token=...` é redirecionado para `/confirmar-email/?token=...` mantendo a query, então o link do e-mail funciona sem mudar o `CONFIRMACAO_URL_BASE`. Isso precisa ser conferido em T2. |
| Endereço da API | Constante `API_BASE_URL` em `front/js/config.js`, padrão `http://127.0.0.1:5000`. | Um único ponto de configuração, sem número mágico espalhado. |
| CORS | O backend já lê `CORS_ORIGINS`. Em dev, usar `CORS_ORIGINS=http://localhost:5173`. Nenhuma mudança de código em `server/`. | O front roda em outra origem. |
| Sessão no navegador | Guardar `{token, expira_em}` em `localStorage`. Antes de usar, conferir `expira_em`. Se vencido ou se a API responder `401`, apagar e mandar para `/entrar/`. | O backend usa token opaco no header `Authorization: Bearer` (spec 001). O `localStorage` mantém a sessão entre abas e recargas até ela expirar. O risco de XSS é reduzido pela regra de nunca usar `innerHTML` (RN7). |
| Confirmação | A página `/confirmar-email/` lê o `token` da query e só chama `POST /auth/confirmacao` quando a pessoa clica em confirmar (RN5). | Filtros de e-mail abrem os links automaticamente. |
| Inserção de dados no DOM | Só `textContent`, `value` e criação de elementos. **Proibido `innerHTML`** com dados de usuário ou da API. | RN7 e o `ROTEIRO.md`. |
| Testes | `node --test` (runner nativo do Node, versão 18 ou mais nova; testado com a 24) nos módulos sem DOM, com `fetch` e `localStorage` falsos injetados. As telas (DOM) são conferidas por um roteiro de teste manual. | Não precisa de nenhuma dependência. A lógica que decide o que mostrar fica fora do DOM e pode ser testada como os use cases do backend. |

## Arquitetura do front-end

A mesma ideia do backend: as dependências apontam para dentro, e a lógica que
decide o que mostrar não conhece o DOM nem o `fetch`.

```text
front/
├── index.html                 # redireciona para /inicio/ ou /entrar/
├── entrar/index.html
├── cadastro/index.html
├── confirmar-email/index.html
├── inicio/index.html          # página inicial logada provisória (nome + sair)
├── guia-de-estilo/index.html  # demonstração de todos os componentes do tema
├── css/
│   ├── tema.css               # tokens e componentes comuns a todas as telas do grupo
│   └── acesso.css             # (se precisar) ajustes só das telas de entrada/cadastro
├── package.json               # só {"type": "module", "scripts": {"test": "node --test"}}
├── js/
│   ├── config.js              # API_BASE_URL
│   ├── dominio/
│   │   ├── regras_cadastro.js # domínios aceitos, senha mínima, nome de usuário sem @, obrigatórios
│   │   └── mensagens.js       # textos das telas (validação local, conexão, bloqueio)
│   ├── fluxos/                # "use cases" da interface: recebem dependências, devolvem um estado de tela
│   │   ├── entrar.js
│   │   ├── cadastrar.js
│   │   ├── confirmar_email.js
│   │   ├── reenviar_confirmacao.js
│   │   └── sessao_atual.js    # usuário logado (GET /auth/me) e sair (POST /auth/logout)
│   ├── adaptadores/
│   │   ├── cliente_http.js    # fetch → {status, corpo} ou ErroDeConexao
│   │   ├── auth_api.js        # uma função por rota /auth/*
│   │   └── armazenamento_sessao.js  # localStorage: salvar, ler (com expiração), apagar
│   └── paginas/               # só DOM: lê o formulário, chama o fluxo, desenha o estado
│       ├── comum.js           # helpers: mostrar erro no campo, estado de carregando, aria-live
│       ├── entrar.js
│       ├── cadastro.js
│       ├── confirmar_email.js
│       └── inicio.js
└── tests/                     # node --test
    ├── fakes.js               # fetch falso e armazenamento em memória
    ├── regras_cadastro.test.js
    ├── cliente_http.test.js
    ├── armazenamento_sessao.test.js
    ├── entrar.test.js
    ├── cadastrar.test.js
    ├── confirmar_email.test.js
    ├── reenviar_confirmacao.test.js
    └── sessao_atual.test.js
```

Direção das dependências:

```text
paginas/ → fluxos/ → dominio/
paginas/ → adaptadores/ (montagem)    fluxos/ recebem os adaptadores por parâmetro
```

- `dominio/` não importa nada.
- `fluxos/` importam `dominio/` e recebem `authApi` e `armazenamentoSessao` por
  parâmetro (injeção de dependência), como os use cases do backend. Assim os
  testes passam dublês.
- `paginas/` é a única camada que mexe no DOM e a única que monta os
  adaptadores concretos.

## Contrato usado (spec 001, sem mudanças)

Erros vêm como `{"message": str, "code"?: str}`.

| Fluxo | Rota | Resposta → estado da tela |
|---|---|---|
| `entrar` | `POST /auth/login` `{identificador, senha}` | `200 {token, expira_em}` → salva a sessão e vai para `/inicio/` (CA2). `401` → "Credenciais inválidas" e apaga a senha (CA3). `403` com `code=email_nao_confirmado` → aviso e botão de reenvio (CA4). `429` → aviso de bloqueio (CA5). `400` → mensagem do servidor. |
| `cadastrar` | `POST /auth/cadastro` `{nome, email, nome_usuario, vinculo, senha, matricula?}` | `201` → tela "verifique seu e-mail" com o endereço (CA12). `400`/`409` → mensagem do servidor, mantendo os campos e apagando a senha (CA13). |
| `reenviar_confirmacao` | `POST /auth/confirmacao/reenviar` `{email}` | `202 {message}` → mostra a mensagem genérica do servidor (RN4). |
| `confirmar_email` | `POST /auth/confirmacao` `{token}` | `200` → sucesso (CA15). `410` → expirado, com formulário de reenvio (CA16). `400` → link inválido (CA17). |
| `sessao_atual` | `GET /auth/me` com Bearer | `200` → mostra o nome. `401` → apaga a sessão e vai para `/entrar/` com aviso (CA21). |
| `sessao_atual.sair` | `POST /auth/logout` com Bearer | `204` ou `401` → apaga a sessão e vai para `/entrar/` (CA22). |
| qualquer um | — | Falha de rede (`fetch` rejeita) → `ErroDeConexao` → mensagem de conexão, mantendo os campos (CA24). |

`matricula` vazia não é enviada (ou vai como `null`). `vinculo` usa os valores
`aluno` e `funcionario`, com os rótulos "Aluno" e "Funcionário".

## Validação local (RN2)

`dominio/regras_cadastro.js` expõe `validarCadastro(dados)` e
`validarLogin(dados)`, que devolvem um mapa `campo → mensagem` (vazio quando
está tudo certo). Constantes com nome: `DOMINIOS_INSTITUCIONAIS =
["puc-rio.br", "aluno.puc-rio.br"]` e `TAMANHO_MINIMO_SENHA = 8`, espelhando
`server/core/entities/`. O e-mail é comparado sem diferenciar maiúsculas de
minúsculas e sem espaços nas pontas. Como o servidor continua validando,
uma diferença entre as duas regras só faz a tela mostrar o erro do servidor.

`validarCadastro` também confere que `confirmacao_senha` é igual a `senha`
(CA11a). A confirmação nunca é enviada à API.

## Visual (`front/css/tema.css`, CA28)

Valores tirados do CSS do login do Ambiente de Aprendizagem On-line da PUC-Rio
(`ead.puc-rio.br/loginccead/style/styles.css`), lido em 2026-11-20:

| Token | Valor | Origem |
|---|---|---|
| `--fonte-base` | Rethink Sans (Google Fonts) | login EAD |
| `--cor-fundo` | `#f8f8f8` | login EAD |
| `--cor-primaria` / `--cor-primaria-escura` | `#213f7c` / `#030053` (hover) | botão de entrar do EAD |
| `--cor-link` | `#273a7c` | "Esqueceu a senha" do EAD |
| `--cor-destaque-contorno` | `#0d47a1` | botão "Atendimento" do EAD |
| `--cor-titulo-marca`, `--cor-texto-rotulo`, `--cor-borda`, `--cor-divisor` | `#777`, `#333`, `#ccc`, `#6c757d` | login EAD |
| `--raio-campo` / `--raio-pilula` | `5px` / pílula | login EAD |
| `--cor-preco`, `--cor-selo`, estados de erro/sucesso/aviso | próprios | classificados |

Componentes: `.cabecalho` e `.navegacao` (barra branca com item ativo
sublinhado, como no painel do EAD), `.acesso` (marca | divisor | formulário,
em coluna no celular), `.formulario`/`.campo`/`.campo-senha` (com o botão
`.campo-senha__alternar`), `.botao--primario|--contorno|--texto`,
`.alerta--erro|--sucesso|--aviso|--info`, `.painel`, `.grade-anuncios`,
`.anuncio` (imagem, etiqueta, preço, título, meta), `.etiqueta` e `.filtro`.

Regras para o grupo: usar as variáveis de `:root`, nunca cores ou medidas
soltas; reaproveitar as classes antes de criar novas; estilos de uma tela só
em um CSS da própria tela. A marca é texto ("PUC | Classificados"), sem o
logotipo oficial.

O botão mostrar/ocultar (CA27) é um `<button type="button">` com texto
"Mostrar"/"Ocultar" e `aria-pressed`, que troca o `type` do campo entre
`password` e `text`. Fica em `paginas/comum.js`, para todas as senhas.

## Acessibilidade e layout (CA25, CA26)

- `<label for>` em todos os campos; `autocomplete` adequado (`username`,
  `current-password`, `new-password`, `email`, `name`).
- Erro de campo em um elemento ligado por `aria-describedby`, com
  `aria-invalid="true"` no campo e foco no primeiro campo com erro.
- Mensagens gerais em uma região `role="alert"` / `aria-live`.
- Botão em envio: `disabled` e texto "Entrando…" / "Cadastrando…" (CA23).
- CSS com variáveis em `:root`, layout em coluna única com `max-width` e
  margens laterais de 16 px, sem largura fixa (sem rolagem horizontal no celular).

## Mudanças fora de `front/`

- `ARQUITETURA.md`: trocar "o projeto de interface `front/` é externo a este
  repositório" pela estrutura de `front/` e sua regra de dependências, e
  atualizar a linha "UI" e o diagrama.
- `ROTEIRO.md` (seção 12): registrar que o front agora fica em `front/`.
- `README.md`: como subir o front (`make front`), `CORS_ORIGINS` em dev e
  `make front-test`.
- `Makefile`: alvos `front` (servidor na porta 5173) e `front-test`
  (`node --test` em `front/`).
- `server/`: **nenhuma mudança de código**.

## Princípios aplicados

- **Clean Architecture:** `dominio/` e `fluxos/` não conhecem DOM, `fetch` nem
  `localStorage`. Trocar o armazenamento da sessão ou o cliente HTTP é mexer só
  em `adaptadores/`.
- **S:** um fluxo por ação de tela; cada página só desenha o estado.
- **D:** os fluxos recebem `authApi` e `armazenamentoSessao` por parâmetro.
- **Clean Code:** constantes com nome para domínios, tamanho de senha, chave do
  `localStorage` e URL da API; erros explícitos (`ErroDeConexao`), sem
  `catch` silencioso.

## Estratégia de testes

- `regras_cadastro.test.js`: cada regra com caso de sucesso e de falha (CA6,
  CA8–CA11), incluindo maiúsculas e espaços no e-mail.
- `cliente_http.test.js`: monta a URL com `API_BASE_URL`, envia JSON e o header
  Bearer quando houver token, devolve `{status, corpo}`, transforma a rejeição
  do `fetch` em `ErroDeConexao`.
- `armazenamento_sessao.test.js`: salva e lê; sessão com `expira_em` no passado
  é tratada como ausente e apagada.
- Fluxos (com `fetch` falso e armazenamento em memória): cada linha da tabela
  "Contrato usado", incluindo a falha de conexão.
- Roteiro manual (T19) com backend real e `EMAIL_BACKEND=log`, cobrindo as
  telas e o que não dá para testar sem DOM (foco, teclado, celular).

### Mapa critério → teste

| CA | Onde é testado |
|---|---|
| CA1, CA7 | manual |
| CA2 | `entrar.test.js` (200 salva sessão e pede navegação) + manual |
| CA3 | `entrar.test.js` (401) + manual (senha apagada) |
| CA4 | `entrar.test.js` (403 `email_nao_confirmado`) + `reenviar_confirmacao.test.js` |
| CA5 | `entrar.test.js` (429) |
| CA6 | `regras_cadastro.test.js` (`validarLogin`) + `entrar.test.js` (não chama a API) |
| CA8–CA11, CA11a | `regras_cadastro.test.js` + `cadastrar.test.js` (não chama a API; a confirmação não vai no corpo) |
| CA12 | `cadastrar.test.js` (201) + manual |
| CA13 | `cadastrar.test.js` (409 e 400) + manual |
| CA14 | manual (abrir o link não chama a API) |
| CA15–CA17 | `confirmar_email.test.js` (200, 410, 400) |
| CA18 | `confirmar_email.test.js` (sem token não chama a API) + manual |
| CA19, CA20 | `sessao_atual.test.js` (com e sem sessão salva) + manual |
| CA21 | `sessao_atual.test.js` (401 e sessão expirada apagam a sessão) |
| CA22 | `sessao_atual.test.js` (sair apaga a sessão com 204 e com 401) |
| CA23 | manual |
| CA24 | `cliente_http.test.js` + um teste por fluxo com `ErroDeConexao` |
| CA25, CA26, CA27, CA28 | manual |

## Link de confirmação fora da máquina local

O `CONFIRMACAO_URL_BASE` é lido pelo backend que envia o e-mail. Cada pessoa
que roda o projeto na própria máquina recebe links para o próprio
`localhost:5173`, o que funciona. Um link com `localhost` aberto em outra
máquina aponta para essa outra máquina, então não funciona se alguém usar o
backend de outra pessoa. Para testes compartilhados ou produção, basta
publicar o front e definir `CONFIRMACAO_URL_BASE=https://<endereço-do-front>/confirmar-email`
e `CORS_ORIGINS=https://<endereço-do-front>` no backend. Não precisa mudar
código. O deploy está fora desta feature.
