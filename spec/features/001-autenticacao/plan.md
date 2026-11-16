# Plano técnico: Autenticação de membros PUC

Referência: `spec.md` desta pasta.

Escopo das subtasks cobertas por este plano:

- [Back-end] Configurar serviço de envio de e-mail (token/link mágico).
- [Back-end] Criar rotas de autenticação, geração e validação de JWT.

## Domain (`domain/`)

| Entidade / objeto | Atributos | Regras/validações |
|-------------------|-----------|-------------------|
| `Usuario` | id, nome, email, matricula, vinculo, senha_hash | `pode_acessar()` só é verdadeiro para vínculo aluno ou funcionário (RN3) |
| `email_institucional` (módulo) | `DOMINIOS_INSTITUCIONAIS` = aluno.puc-rio.br, puc-rio.br | `validar_email_institucional(email)` normaliza (minúsculas, sem espaços nas pontas) e aceita só os domínios exatos (RN2) |
| `Vinculo` (enum) | ALUNO, FUNCIONARIO, TERCEIRIZADO | — |
| `PoliticaBloqueio` | max_tentativas=5, duracao=10 min | parâmetros do bloqueio (RN4) |
| `TentativasLogin` | falhas_consecutivas, bloqueado_ate | `esta_bloqueado(agora)`; `registrar_falha(agora, politica)` bloqueia na 5ª falha e recomeça a contagem depois que um bloqueio termina |
| `LinkMagico` | token_hash, usuario_id, expira_em, usado | `pode_ser_usado(agora)` (RN7) |

Erros de domínio (`domain/erros.py`): `CredenciaisInvalidas`,
`LoginBloqueado(segundos_restantes)`, `EmailNaoInstitucional`,
`TokenInvalido`.

## Use cases (`use_cases/autenticacao/`)

| Use case | Entrada | Saída | Erros possíveis |
|----------|---------|-------|-----------------|
| `EntrarComEmail` | email, senha | `SessaoAutenticada` (token, expira_em_segundos) | `EmailNaoInstitucional`, `CredenciaisInvalidas`, `LoginBloqueado` |
| `SolicitarLinkMagico` | email | nada (sempre igual para e-mails institucionais, RN6) | `EmailNaoInstitucional` |
| `EntrarComLinkMagico` | token | `SessaoAutenticada` | `TokenInvalido` |
| `ObterUsuarioAutenticado` | token de sessão | `Usuario` | `TokenInvalido` |

Interfaces (`use_cases/autenticacao/portas.py`), todas pequenas (ISP):

- `UsuarioRepository`: `buscar_por_email`, `buscar_por_id`.
- `TentativasLoginRepository`: `obter`, `salvar`, `limpar` (chave: e-mail
  normalizado).
- `LinkMagicoRepository`: `salvar`, `buscar_por_token_hash`,
  `marcar_como_usado`.
- `VerificadorSenha`: `verificar(senha, senha_hash)`.
- `ServicoToken`: `emitir(usuario_id)`, `validar(token) -> usuario_id`.
- `EnviadorEmail`: `enviar(destinatario, assunto, corpo)`.
- `Relogio`: `agora()` — permite testar expiração e bloqueio.

## Infra (`infra/`)

- `infra/seguranca/servico_token_jwt.py`: JWT HS256 com PyJWT, segredo e
  validade vindos da configuração.
- `infra/seguranca/verificador_senha_werkzeug.py`: hash com
  `werkzeug.security` (já vem com o Flask, sem dependência nova).
- `infra/email/enviador_email_smtp.py`: SMTP com `smtplib` (biblioteca
  padrão), configurado por variáveis de ambiente.
- `infra/email/enviador_email_console.py`: escreve o e-mail no log; padrão em
  desenvolvimento quando `SMTP_HOST` não está definido.
- `infra/repositories/memoria.py`: repositórios em memória para usuários,
  tentativas e links mágicos.
- `infra/relogio_sistema.py`: relógio real (UTC).

Pendência de modelagem: a tabela `usuarios` não tem `senha_hash`, e não há
tabelas para tentativas e links. Até essa mudança ser aprovada, a aplicação
usa os repositórios em memória. Os repositórios SQLite entram quando o schema
for atualizado (skill `manter-modelagem-dados`).

## Interface web (`app/routes/autenticacao.py`)

| Método | Rota | Use case chamado | Resposta |
|--------|------|------------------|----------|
| POST | `/auth/login` | `EntrarComEmail` | 200 `{access_token, token_type, expires_in}`; 400 campos faltando ou e-mail não institucional; 401 `{"erro": "E-mail ou senha inválidos"}`; 429 bloqueado, com `Retry-After` |
| POST | `/auth/link-magico` | `SolicitarLinkMagico` | 202 para qualquer e-mail institucional (RN6); 400 sem e-mail ou e-mail não institucional; 503 falha no envio |
| POST | `/auth/link-magico/validar` | `EntrarComLinkMagico` | 200 com token; 401 link inválido |
| GET | `/auth/me` | `ObterUsuarioAutenticado` | 200 dados do usuário; 401 sem token válido |

O decorator `requer_autenticacao` (em `app/routes/autenticacao.py`) lê
`Authorization: Bearer <token>` e pode proteger outras rotas, como o feed.

A montagem das dependências fica em `app/main.py` (`create_app`), que aceita
um dicionário de configuração e dependências opcionais para os testes.

Configuração (variáveis de ambiente): `JWT_SECRET`, `JWT_EXPIRA_MINUTOS`
(padrão 60), `URL_LINK_MAGICO`, `SMTP_HOST`, `SMTP_PORT`, `SMTP_USUARIO`,
`SMTP_SENHA`, `SMTP_REMETENTE`.

## Princípios SOLID aplicados

- **S**: um use case por ação; envio de e-mail, tokens e hash ficam em
  classes separadas.
- **O**: trocar SMTP por outro provedor é criar outra classe que cumpre
  `EnviadorEmail`.
- **L**: repositórios em memória e futuros repositórios SQLite são
  intercambiáveis.
- **I**: portas pequenas, cada use case recebe só o que usa.
- **D**: use cases recebem as portas por injeção; `create_app` monta tudo.

## Estratégia de testes

- `tests/domain/`: `validar_email_institucional`, `PoliticaBloqueio`,
  `Usuario.pode_acessar`, `LinkMagico.pode_ser_usado`.
- `tests/use_cases/`: cada use case com falsos em memória e relógio
  controlado (CA1–CA8).
- `tests/infra/`: JWT (emissão, expiração, assinatura errada), hash de senha,
  enviador SMTP com `smtplib.SMTP` substituído por um falso.
- `tests/app/`: rotas com o cliente de teste do Flask (status, mensagens,
  `Retry-After`, decorator).
