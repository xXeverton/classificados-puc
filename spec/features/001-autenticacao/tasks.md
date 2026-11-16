# Tarefas: Autenticação de membros PUC

Referências: `spec.md` e `plan.md` desta pasta.
Marque `[x]` ao concluir. Escreva os testes antes da implementação.

## Domain

- [x] T1: Testes de `Usuario`, `PoliticaBloqueio` e `LinkMagico` em
  `tests/domain/`
- [x] T2: Implementar entidades e erros em `domain/`
- [x] T2.1: Testes e regra de e-mail institucional
  (`domain/email_institucional.py`)

## Use cases

- [x] T3: Definir as portas em `use_cases/autenticacao/portas.py`
- [x] T4: Testes de `EntrarComEmail` (CA1–CA5)
- [x] T5: Implementar `EntrarComEmail`
- [x] T6: Testes de `SolicitarLinkMagico` e `EntrarComLinkMagico` (CA5–CA7)
- [x] T7: Implementar os use cases de link mágico
- [x] T8: Testes e implementação de `ObterUsuarioAutenticado` (CA8)

## Infra

- [x] T9: Serviço JWT com PyJWT e testes
- [x] T10: Verificador de senha com `werkzeug.security` e testes
- [x] T11: Enviador de e-mail SMTP e de console, com testes
- [x] T12: Repositórios em memória e relógio do sistema
- [ ] T13: Repositórios SQLite (bloqueado: aguarda `senha_hash` e tabelas de
  tentativas/links no schema)

## Web

- [x] T14: Rotas em `app/routes/autenticacao.py` e decorator
  `requer_autenticacao`
- [x] T15: Montagem das dependências em `app/main.py`
- [x] T16: Testes das rotas em `tests/app/`

## Validação

- [x] T17: `pytest` passando
- [x] T18: `flake8` sem erros
- [ ] T19: Critérios de aceitação conferidos com o PO
- [ ] T20: Definir o papel do link mágico agora que o login é por e-mail +
  senha (acesso alternativo, recuperação de senha ou remover)
- [ ] T21: Confirmar com o PO a mensagem "E-mail ou senha inválidos" e o
  wireframe com campo de e-mail
