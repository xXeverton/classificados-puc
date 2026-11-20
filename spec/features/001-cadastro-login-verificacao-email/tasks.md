# Tarefas: Cadastro, login e verificação de e-mail institucional

Referências: `spec.md` e `plan.md` desta pasta. Jira: PROJ-23.
Marque `[x]` ao concluir. Escreva os testes antes da implementação.
Rode `pytest` ao fim de cada bloco.

## 0. Preparação

- [x] T0: Confirmar com o time a estratégia de migração do banco local
  (`plan.md` → Migração): recriar o banco local, sem script de migração.

## 1. Domain (`server/core/entities/`)

- [x] T1: Testes de `validar_senha` (7 caracteres recusa, 8 aceita).
  Implementar `senha.py` com `TAMANHO_MINIMO_SENHA`. (CA4)
- [x] T2: Criar `politicas_autenticacao.py` com as constantes de validade do
  token (15 min), máximo de tentativas (5) e duração do bloqueio (10 min), e
  `hash_de_token` (SHA-256), com teste.
- [x] T3: Testes de `Vinculo` (aceita `aluno`/`funcionario`, recusa outros).
  Implementar o `Enum`. (CA5)
- [x] T4: Ajustar `tests/core/entities/test_usuario.py` com um helper de
  fábrica e escrever os testes novos: `nome_usuario` obrigatório e sem `@`;
  matrícula opcional (vazia vira `None`); nome obrigatório; normalização de
  email/nome_usuario/matricula. (CA5, CA7, CA8)
- [x] T5: Testes de estado da conta: `esta_confirmado`, `confirmar`,
  `registrar_falha_de_login` (bloqueia na 5ª e zera a contagem),
  `esta_bloqueado` (antes e depois de 10 min), `registrar_login_bem_sucedido`
  (zera a contagem). (CA21)
- [x] T6: Implementar as mudanças em `Usuario` até T4 e T5 passarem.
- [x] T7: Testes e implementação de `TokenDeConfirmacao` (`esta_valido`,
  `usar`) e `Sessao` (`esta_ativa`, `revogar`). (CA13, CA14, CA22)

## 2. Interfaces e dublês de teste

- [x] T8: Ampliar `UsuarioRepositoryInterface` (`buscar_por_email`,
  `buscar_por_identificador_alternativo`, `remover`) e criar
  `TokenDeConfirmacaoRepositoryInterface`, `SessaoRepositoryInterface`,
  `EnviadorDeEmailInterface`, `HasherDeSenhaInterface`,
  `GeradorDeTokenInterface` e `RelogioInterface`.
- [x] T9: Criar `tests/core/usecases/fakes.py` com repositórios em memória,
  `RelogioFalso`, `EnviadorDeEmailFalso`, `GeradorDeTokenFalso` e
  `HasherDeSenhaFalso`.
- [x] T10: Adicionar os erros de caso de uso em `erros.py` (`DadosInvalidos`,
  `EmailEmUso`, `IdentificadorEmUso`, `TokenInvalido`, `TokenExpirado`,
  `CredenciaisInvalidas`, `ContaBloqueada`, `EmailNaoConfirmado`,
  `SessaoInvalida`).

## 3. Use cases (`server/core/usecases/`)

- [x] T11: Testes de `EmissorDeConfirmacao`: gera o token, guarda só o hash
  com validade de 15 min, invalida os anteriores e envia o e-mail com o link
  `CONFIRMACAO_URL_BASE?token=...`. Implementar.
- [x] T12: Testes de `CadastrarUsuario`: sucesso cria pendente e envia e-mail
  (CA1); domínio inválido (CA2); e-mail de conta confirmada (CA3); senha curta
  (CA4); dados inválidos (CA5); nome de usuário em uso (CA6); sem matrícula
  (CA8); matrícula em uso (CA9); nome de usuário = matrícula de outra conta e
  o inverso (CA10); substitui pendente e invalida links antigos (CA11);
  identificador de pendente sem token válido é liberado e com token válido
  continua em uso (RN13).
- [x] T13: Implementar `CadastrarUsuario` até T12 passar.
- [x] T14: Testes de `ConfirmarEmail`: sucesso (CA12), expirado (CA13), já
  usado ou inexistente (CA14). Implementar.
- [x] T15: Testes de `ReenviarConfirmacao`: conta pendente recebe link novo e
  o antigo deixa de valer (CA15); e-mail inexistente ou já confirmado não
  envia nada e não gera erro. Implementar.
- [x] T16: Testes de `Autenticar`: login por e-mail, nome de usuário e
  matrícula (CA16–CA18); pendente com senha certa (CA19); identificador
  inexistente e senha errada dão o mesmo erro (CA20); 5 falhas bloqueiam, o
  bloqueio vale para qualquer identificador, tentativas durante o bloqueio não
  contam, e o login volta a funcionar após 10 min (CA21); login certo zera a
  contagem.
- [x] T17: Implementar `Autenticar` até T16 passar.
- [x] T18: Testes de `EncerrarSessao` e `ObterUsuarioDaSessao`: sessão
  revogada, expirada e inexistente geram `SessaoInvalida` (CA22, CA23).
  Implementar.

## 4. Infra (`server/infra/`) — seguir a skill `manter-modelagem-dados`

- [x] T19: Testes de banco em `tests/infra/db/test_database.py`: novas colunas
  de `usuarios`; `matricula` aceitando vários `NULL` mas única quando
  preenchida; `CHECK` de `@` em `nome_usuario`; `CHECK` de `vinculo`; tabelas
  `tokens_confirmacao` e `sessoes`; cascade ao remover usuário; pragma
  `foreign_keys` ativo.
- [x] T20: Atualizar `models.py`, `schema.sql` e `database.py` (pragma
  `foreign_keys`) até T19 passar.
- [x] T21: Atualizar `server/infra/db/README.md` (diagrama com as 3 tabelas,
  tabela de colunas, matrícula opcional, instrução de migração definida em T0).
- [x] T22: Testes e implementação do `UsuarioRepositorySQLAlchemy` ampliado
  (`buscar_por_email`, `buscar_por_identificador_alternativo` nas duas
  colunas, `remover`, persistência dos novos campos).
- [x] T23: Testes e implementação de `TokenConfirmacaoRepositorySQLAlchemy` e
  `SessaoRepositorySQLAlchemy`.
- [x] T24: Testes e implementação dos serviços em `server/infra/services/`:
  `HasherDeSenhaWerkzeug` (hash diferente da senha; verifica certo e errado),
  `GeradorDeTokenSecrets`, `RelogioSistema` (UTC), `EnviadorDeEmailLog`
  (`caplog`) e `EnviadorDeEmailSMTP` (com `smtplib.SMTP` substituído por um
  dublê, sem rede, conferindo STARTTLS, login e mensagem).

## 5. Web (`server/api/`)

- [x] T25: Schemas pydantic de entrada e presenters (`usuario_presenter`, sem
  `senha_hash`; `sessao_presenter`).
- [x] T26: Testes de API em `tests/api/test_auth_controller.py` para cada
  rota e código de status do `plan.md`, incluindo o fluxo completo cadastro →
  confirmação (token lido do `EnviadorDeEmailFalso`) → login → `/auth/me` →
  logout → `/auth/me` com `401`.
- [x] T27: Implementar `auth_controller.py` e o decorator `exige_sessao` em
  `server/api/autenticacao.py` até T26 passar. (CA23)
- [x] T28: Montar as dependências em `server/app.py` (escolha do enviador por
  `EMAIL_BACKEND`, falha clara se `smtp` estiver sem configuração) e permitir
  substituir relógio, enviador e gerador de token pelo `config` nos testes.

## 6. Documentação

- [x] T29: Documentar no `README.md` raiz as variáveis `EMAIL_BACKEND`,
  `SMTP_*`, `EMAIL_REMETENTE`, `CONFIRMACAO_URL_BASE` e
  `SESSAO_DURACAO_HORAS`, e como ver o link de confirmação no log em dev.
- [x] T30: Registrar em `ARQUITETURA.md` que toda rota de conteúdo deve usar
  `exige_sessao`.

## 7. Validação

- [x] T31: `pytest` passando.
- [x] T32: `flake8` sem erros.
- [x] T33: Conferir o mapa critério → teste do `plan.md`: todos os CA1–CA23
  com teste passando. Marcar os critérios na `spec.md` e mudar o status para
  `Implementada`.
- [ ] T34: Teste manual com `EMAIL_BACKEND=smtp` enviando para um endereço
  `@puc-rio.br` real, para conferir a entrega e o filtro anti-spam da
  universidade.
