# Plano técnico: Cadastro, login e verificação de e-mail institucional

Referência: `spec.md` desta pasta (CA1–CA23, RN1–RN14).

## Decisões técnicas

| Tema | Decisão | Motivo |
|---|---|---|
| Sessão | Token de sessão **opaco**, aleatório, enviado no header `Authorization: Bearer <token>`. O banco guarda só o hash SHA-256 do token, com validade e data de revogação. | Logout revoga a sessão no servidor (CA22), sem dependência nova. O front-end é separado (CORS), e o header evita a configuração de cookies entre origens. Um JWT continuaria válido depois do logout. |
| Hash de senha | `werkzeug.security` (`generate_password_hash` / `check_password_hash`), que já vem com o Flask. | Algoritmo com salt e custo ajustável, sem dependência nova. |
| Token de confirmação | `secrets.token_urlsafe(32)`. O banco guarda só o hash SHA-256. | Quem lê o banco não consegue usar o link. |
| Link de confirmação | Aponta para uma página do front-end (`CONFIRMACAO_URL_BASE?token=...`), que chama `POST /auth/confirmacao`. **Não** existe um `GET` que confirma direto. | Filtros de e-mail (ex.: Microsoft Safe Links, usado pela PUC-Rio) abrem os links automaticamente e consumiriam o token de uso único. |
| Envio de e-mail | Interface no core e duas implementações: `log` (dev/testes) e `smtp` (`smtplib` com STARTTLS). Escolha por `EMAIL_BACKEND`. | Decisão registrada na spec. Sem dependência nova. |
| Tempo | Interface `RelogioInterface`, com horários sempre em UTC. | Testes de expiração (CA13) e de bloqueio (CA21) sem `sleep`. |
| Chave da tabela | `id` inteiro continua como chave primária técnica. `email` é a chave de negócio, única e obrigatória (RN8). | Mantém a decisão documentada em `server/infra/db/README.md` e evita propagar o e-mail para chaves estrangeiras. |
| Maiúsculas/minúsculas | `email`, `nome_usuario` e `matricula` são gravados normalizados (sem espaços nas pontas, em minúsculas). | Unicidade e busca sem diferenciar caixa (RN1, RN12) usando constraints simples. |
| Unicidade cruzada (RN12) | Conferida no caso de uso, antes de salvar, com uma busca que olha `nome_usuario` **e** `matricula`. As constraints `UNIQUE` de cada coluna continuam no banco. | O SQLite não tem constraint entre colunas diferentes. No MVP, aceitamos a pequena janela de concorrência entre dois cadastros simultâneos. |

### Configuração (variáveis de ambiente)

| Variável | Padrão | Uso |
|---|---|---|
| `EMAIL_BACKEND` | `log` | `log` ou `smtp` |
| `SMTP_HOST`, `SMTP_PORT`, `SMTP_USUARIO`, `SMTP_SENHA` | — | Obrigatórias quando `EMAIL_BACKEND=smtp` |
| `EMAIL_REMETENTE` | — | Endereço "De:" (obrigatória com `smtp`) |
| `CONFIRMACAO_URL_BASE` | `http://localhost:5173/confirmar-email` | Página do front-end que recebe `?token=` |
| `SESSAO_DURACAO_HORAS` | `8` | Validade da sessão (padrão confirmado em 2026-11-20; ajustável) |

Segredos SMTP só entram por variável de ambiente, nunca no repositório.

## Entities (`server/core/entities/`)

| Entidade | Atributos | Regras/validações |
|----------|-----------|-------------------|
| `Usuario` (alterada) | `id`, `nome`, `email`, `nome_usuario`, `matricula: str \| None`, `vinculo: Vinculo`, `senha_hash`, `confirmado_em: datetime \| None`, `tentativas_login_falhas: int`, `bloqueado_ate: datetime \| None` | E-mail institucional (RN1, já existente); nome não vazio; `nome_usuario` não vazio e sem `@` (RN11); `matricula` vazia vira `None`; normaliza email/nome_usuario/matricula. Métodos puros que devolvem uma nova instância (a dataclass é imutável): `esta_confirmado()`, `esta_bloqueado(agora)`, `confirmar(agora)`, `registrar_falha_de_login(agora)` (na 5ª falha, bloqueia por 10 min e zera a contagem, RN5), `registrar_login_bem_sucedido()`. |
| `Vinculo` (nova, `Enum`) | `ALUNO = "aluno"`, `FUNCIONARIO = "funcionario"` | Valor fora da lista gera erro (CA5, RN7). |
| `TokenDeConfirmacao` (nova) | `id`, `usuario_id`, `token_hash`, `expira_em`, `usado_em: datetime \| None` | `esta_valido(agora)`: não usado e não expirado (RN3). `usar(agora)`. |
| `Sessao` (nova) | `id`, `usuario_id`, `token_hash`, `expira_em`, `revogada_em: datetime \| None` | `esta_ativa(agora)`, `revogar(agora)`. |

Regras auxiliares puras em `server/core/entities/`:

- `senha.py`: `TAMANHO_MINIMO_SENHA = 8` e `validar_senha(senha)` (RN4, CA4). A senha em texto puro nunca é guardada na entidade.
- `politicas_autenticacao.py`: `VALIDADE_TOKEN_CONFIRMACAO = timedelta(minutes=15)`, `MAXIMO_TENTATIVAS_LOGIN = 5`, `DURACAO_BLOQUEIO_LOGIN = timedelta(minutes=10)`.
- `hash_de_token(token) -> str`: SHA-256 em hexadecimal (`hashlib`, biblioteca padrão).

## Use cases (`server/core/usecases/`)

| Use case | Entrada | Saída | Erros possíveis |
|----------|---------|-------|-----------------|
| `CadastrarUsuario` | nome, email, nome_usuario, matricula?, vinculo, senha | `Usuario` pendente | `DadosInvalidos` (CA2, CA4, CA5, CA7), `EmailEmUso` (CA3), `IdentificadorEmUso` (CA6, CA9, CA10) |
| `ConfirmarEmail` | token | `Usuario` confirmado | `TokenInvalido` (inexistente ou já usado, CA14), `TokenExpirado` (CA13) |
| `ReenviarConfirmacao` | email | — | Nenhum visível: responde igual para e-mail inexistente ou já confirmado, para não revelar contas |
| `Autenticar` | identificador, senha | token da sessão + `expira_em` | `CredenciaisInvalidas` (CA20), `ContaBloqueada` (CA21), `EmailNaoConfirmado` (CA19) |
| `EncerrarSessao` | token | — | `SessaoInvalida` |
| `ObterUsuarioDaSessao` | token | `Usuario` | `SessaoInvalida` (CA23) |

Colaborador interno: `EmissorDeConfirmacao` invalida os tokens anteriores do usuário, gera o novo, salva o hash e envia o e-mail com o link. É usado por `CadastrarUsuario` e por `ReenviarConfirmacao`, para não duplicar código.

Fluxos principais:

- **Cadastro (RN9, RN13):**
  1. Valida a senha e monta o `Usuario` (as validações da entidade valem aqui).
  2. Se o e-mail pertence a uma conta confirmada, gera `EmailEmUso`. Se pertence a uma conta pendente, os novos dados substituem os dela.
  3. Para `nome_usuario` e `matricula`, busca outra conta que use o valor em **qualquer** das duas colunas. Se a dona for uma conta pendente **sem token válido**, essa conta é removida e o valor fica livre. Caso contrário, gera `IdentificadorEmUso`.
  4. Salva o usuário com `confirmado_em = None` e chama o `EmissorDeConfirmacao`.
- **Login (RN5, RN10, RN14):**
  1. Se o identificador contém `@`, busca pelo e-mail. Senão, busca por `nome_usuario` ou `matricula` (a RN12 garante no máximo um resultado).
  2. Conta inexistente gera `CredenciaisInvalidas`.
  3. Conta bloqueada gera `ContaBloqueada`, sem conferir a senha e sem contar tentativa.
  4. Senha errada: `registrar_falha_de_login`, salva, gera `CredenciaisInvalidas`. Se essa foi a 5ª falha, a conta fica bloqueada a partir daí.
  5. Senha certa e conta pendente gera `EmailNaoConfirmado`. A senha é conferida antes, para não revelar o estado da conta a quem não sabe a senha.
  6. Senha certa e conta confirmada: `registrar_login_bem_sucedido`, cria a `Sessao` e devolve o token.

**Decisão sobre o aviso de bloqueio (confirmada em 2026-11-20):** conta bloqueada recebe uma mensagem própria (`429`), mesmo que isso revele que o identificador tem conta. O cadastro já revela essa informação (CA3, CA6, CA9), então esconder no login não protegeria nada e confundiria quem foi bloqueado. Risco aceito para o MVP: quem conhece o identificador de alguém pode bloquear a conta dessa pessoa por 10 minutos. Se isso virar problema, a solução é limitar tentativas por IP.

Erros novos em `server/core/usecases/erros.py`, todos herdando de `ErroDeCasoDeUso`.

### Interfaces (`server/core/interfaces/`)

- `UsuarioRepositoryInterface` (ampliada): `buscar_por_id`, `buscar_por_email`, `buscar_por_identificador_alternativo(valor)` (procura em `nome_usuario` ou `matricula`), `salvar`, `remover`.
- `TokenDeConfirmacaoRepositoryInterface`: `salvar`, `buscar_por_hash`, `invalidar_do_usuario(usuario_id, agora)`, `existe_valido_do_usuario(usuario_id, agora)`.
- `SessaoRepositoryInterface`: `salvar`, `buscar_por_hash`.
- `EnviadorDeEmailInterface`: `enviar(destinatario, assunto, corpo)`.
- `HasherDeSenhaInterface`: `gerar_hash(senha)`, `verificar(senha, senha_hash)`.
- `GeradorDeTokenInterface`: `gerar() -> str`.
- `RelogioInterface`: `agora() -> datetime` (UTC).

## Infra (`server/infra/`)

### Tabelas/colunas no SQLite

`usuarios` (alterada):

| Coluna | Tipo | Obrigatória | Restrições |
|---|---|---:|---|
| `id` | INTEGER | Sim | PK, autoincremento |
| `nome` | TEXT | Sim | não vazio |
| `email` | TEXT | Sim | `UNIQUE`, não vazio |
| `nome_usuario` | TEXT | Sim | `UNIQUE`, não vazio, `CHECK (instr(nome_usuario, '@') = 0)` |
| `matricula` | TEXT | **Não** (era obrigatória) | `UNIQUE` quando preenchida; não vazia se informada |
| `vinculo` | TEXT | Sim | `CHECK (vinculo IN ('aluno', 'funcionario'))` |
| `senha_hash` | TEXT | Sim | não vazio |
| `confirmado_em` | DATETIME | Não | `NULL` = pendente |
| `tentativas_login_falhas` | INTEGER | Sim | padrão `0`, `>= 0` |
| `bloqueado_ate` | DATETIME | Não | — |

`tokens_confirmacao` (nova): `id` PK, `usuario_id` FK → `usuarios.id` (`ON DELETE CASCADE`), `token_hash` `UNIQUE`, `expira_em`, `usado_em` (nulo).

`sessoes` (nova): `id` PK, `usuario_id` FK → `usuarios.id` (`ON DELETE CASCADE`), `token_hash` `UNIQUE`, `criada_em`, `expira_em`, `revogada_em` (nulo).

O SQLite só aplica `ON DELETE CASCADE` com `PRAGMA foreign_keys=ON`. O `create_database_engine` passa a ativar esse pragma em cada conexão.

### Migração

`create_all` não altera tabelas existentes. A tabela `usuarios` muda de forma incompatível: novas colunas obrigatórias e `matricula` passando a aceitar nulo. Não há ambiente publicado com dados reais, só bancos locais de desenvolvimento.

**Decisão (confirmada em 2026-11-20):** não haverá script de migração. O banco local `server/database/db.sqlite3` deve ser apagado e recriado depois da atualização. Isso fica documentado em `server/infra/db/README.md` e no `README.md` raiz.

### Arquivos

- Modelos SQLAlchemy: `server/infra/db/models.py` (`UsuarioModel` alterado, `TokenDeConfirmacaoModel`, `SessaoModel`).
- `server/infra/db/schema.sql` e `server/infra/db/README.md` sincronizados (skill `manter-modelagem-dados`).
- Gateways em `server/infra/gateways/`: `usuario_repository_sqlalchemy.py` (ampliado), `token_confirmacao_repository_sqlalchemy.py`, `sessao_repository_sqlalchemy.py`.
- Serviços em `server/infra/services/`: `enviador_email_log.py`, `enviador_email_smtp.py`, `hasher_senha_werkzeug.py`, `gerador_token_secrets.py`, `relogio_sistema.py`.

## Interface web (`server/api/controllers/`)

Novo `auth_controller.py`, registrado em `server/app.py`, com schemas pydantic de entrada e presenters em `server/api/presenters/`.

| Método | Rota | Use case chamado | Resposta |
|--------|------|------------------|----------|
| POST | `/auth/cadastro` | `CadastrarUsuario` | `201` usuário público (sem `senha_hash`); `400` dados inválidos; `409` e-mail ou identificador em uso |
| POST | `/auth/confirmacao` | `ConfirmarEmail` | `200`; `400` token inválido ou usado; `410` token expirado |
| POST | `/auth/confirmacao/reenviar` | `ReenviarConfirmacao` | `202` sempre, com mensagem genérica |
| POST | `/auth/login` | `Autenticar` | `200` `{token, expira_em}`; `401` "Credenciais inválidas"; `403` e-mail não confirmado (código `email_nao_confirmado`, para o front oferecer o reenvio); `429` conta bloqueada |
| POST | `/auth/logout` | `EncerrarSessao` | `204`; `401` sem sessão válida |
| GET | `/auth/me` | `ObterUsuarioDaSessao` | `200` usuário público; `401` sem sessão válida |

**Proteção de rotas (CA23, RN6):** `server/api/autenticacao.py` oferece o decorator `exige_sessao`. Ele lê o header `Authorization: Bearer`, chama `ObterUsuarioDaSessao` e responde `401` quando a sessão é inválida. **Toda rota futura de conteúdo (feed, anúncios, eventos) deve usá-lo.** Hoje ficam públicas só `/health` e as rotas de cadastro, confirmação, reenvio e login.

O controller converte os erros do core em respostas HTTP com `apresenta_erro`. Detalhes do Flask não entram no core.

## Composição (`server/app.py`)

`create_app` monta os repositórios, os serviços (escolhendo o enviador por `EMAIL_BACKEND`) e os casos de uso, e entrega tudo ao `register_auth_controller`. O `create_app(config)` aceita substituir `relogio`, `enviador_email` e `gerador_token` nos testes de API.

## Princípios SOLID aplicados

- **S:** um caso de uso por ação. O envio do link fica isolado no `EmissorDeConfirmacao`. Hash de senha, geração de token, relógio e e-mail são serviços separados.
- **O:** trocar o provedor de e-mail (ex.: uma API transacional) é só uma nova implementação de `EnviadorDeEmailInterface`, sem mexer no core.
- **L:** os repositórios em memória dos testes e os SQLAlchemy cumprem as mesmas interfaces e passam pelos mesmos cenários.
- **I:** interfaces pequenas e separadas por responsabilidade (usuário, token, sessão, e-mail, hash, gerador de token, relógio).
- **D:** os casos de uso recebem todas as dependências pelo construtor, e a montagem fica em `server/app.py`.

## Estratégia de testes

- `tests/core/entities/`: validações de `Usuario` (`@` no nome de usuário, matrícula opcional, vínculo, normalização), bloqueio após 5 falhas e liberação após 10 min, `TokenDeConfirmacao.esta_valido`, `Sessao.esta_ativa`, `validar_senha`.
- `tests/core/usecases/`: cada caso de uso com repositórios em memória, `RelogioFalso`, `EnviadorDeEmailFalso` (guarda as mensagens enviadas) e `GeradorDeTokenFalso` (tokens previsíveis). Os dublês ficam em `tests/core/usecases/fakes.py`.
- `tests/infra/`: constraints das novas colunas e tabelas, `UNIQUE` de `matricula` aceitando vários nulos, cascade, gateways (incluindo `buscar_por_identificador_alternativo`), `EnviadorDeEmailLog` (com `caplog`) e `EnviadorDeEmailSMTP` (com `smtplib.SMTP` substituído por um dublê, sem rede).
- `tests/api/`: rotas de `/auth/*` com o app de teste (SQLite em memória e relógio falso), incluindo o fluxo completo de cadastro → confirmação → login → `/auth/me` → logout.

### Mapa critério → teste

| CA | Onde é testado |
|---|---|
| CA1 | use case `CadastrarUsuario` (cria pendente e envia e-mail) + API cadastro |
| CA2 | entidade `Usuario` (já existe) + use case |
| CA3 | use case (e-mail de conta confirmada) |
| CA4 | `validar_senha` + use case |
| CA5 | entidade (nome vazio, vínculo inválido) + use case |
| CA6 | use case (nome de usuário em uso) |
| CA7 | entidade (`@` no nome de usuário) |
| CA8 | entidade + use case (matrícula ausente) |
| CA9 | use case (matrícula em uso) |
| CA10 | use case (nome de usuário = matrícula de outra conta e o inverso) |
| CA11 | use case (substitui pendente, invalida links antigos) |
| CA12 | use case `ConfirmarEmail` (sucesso) |
| CA13 | use case (expirado, com relógio avançado 15 min + 1 s) |
| CA14 | use case (token reutilizado) |
| CA15 | use case `ReenviarConfirmacao` (novo link, antigo inválido) |
| CA16, CA17, CA18 | use case `Autenticar` com e-mail, nome de usuário e matrícula |
| CA19 | use case (pendente com senha certa) + API `403` |
| CA20 | use case (identificador inexistente e senha errada, mesma mensagem) |
| CA21 | entidade + use case (5 falhas bloqueiam, login após 10 min funciona, bloqueio vale para qualquer identificador) |
| CA22 | use case `EncerrarSessao` + API (token deixa de valer em `/auth/me`) |
| CA23 | API `/auth/me` sem token ou com token inválido → `401` |
| RN13 | use case (identificador de pendente sem token válido é liberado; com token válido continua em uso) |

## Impacto em código existente

- `Usuario`: novos campos obrigatórios. Os testes de `tests/core/entities/test_usuario.py` precisam de dados completos (helper de fábrica).
- `tests/infra/db/test_database.py`: o teste "matrícula obrigatória" passa a verificar que ela é opcional, e entram testes para as novas colunas.
- `tests/infra/gateways/test_usuario_repository_sqlalchemy.py`: ajustado aos novos campos.
- `server/infra/db/README.md`: o trecho "A matrícula permanece obrigatória e única" muda para "opcional e única quando informada".
- `README.md` raiz: documentar as variáveis de ambiente de e-mail e sessão.
