# Projeto de Engenharia de Software

API web em **Python + Flask-OpenAPI3** construída com **Clean Architecture**,
**SQLAlchemy + SQLite**, princípios **SOLID**, testes unitários com **pytest**
e desenvolvimento guiado por especificações (**Spec-Driven Development**).

> Trabalho 2 de Engenharia de Software: Arquitetura e Projeto de Software (PUC-Rio).

## Estrutura do projeto

A organização das camadas e o mapa de diretórios estão em
[ESTRUTURA.md](ESTRUTURA.md). O código da API fica em `server/`; as
especificações, os testes e as ferramentas de desenvolvimento ficam na raiz.
As dependências apontam para dentro: `server/api` e `server/infra` dependem de
abstrações em `server/core`, e o core não depende de frameworks.

## Modelagem do banco de dados

Os modelos SQLAlchemy, o schema SQLite e a documentação das tabelas estão em
[server/infra/db/README.md](server/infra/db/README.md). Sempre que dados
persistidos forem adicionados, alterados ou removidos, mantenha os modelos,
schema, documentação, testes e migrações aplicáveis sincronizados.

## Pré-requisitos

- Python 3.11 ou superior
- Git
- GNU Make para os comandos `make`

## Como inicializar o ambiente

### 1. Clonar o repositório

```bash
git clone <url-do-repositorio>
cd projeto_engenharia_de_software
```

### 2. Criar o ambiente virtual

```bash
python -m venv .venv
```

### 3. Ativar o ambiente virtual

Windows (PowerShell):

```powershell
.venv\Scripts\Activate.ps1
```

> Se o PowerShell bloquear a execução do script, rode uma vez:
> `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`

Windows (Git Bash):

```bash
source .venv/Scripts/activate
```

Linux / macOS:

```bash
source .venv/bin/activate
```

### 4. Instalar as dependências

```bash
make install
```

## Executar a aplicação

```bash
flask --app server.app:create_app run --debug
```

A aplicação sobe em http://127.0.0.1:5000. Para conferir, acesse
http://127.0.0.1:5000/health, que deve responder `{"status": "ok"}`.
O banco padrão fica em `server/database/db.sqlite3`; `DATABASE_URL` pode
substituir essa localização. Configure as origens CORS permitidas com
`CORS_ORIGINS`, separadas por vírgula; sem origens configuradas, CORS fica
desabilitado.

> **Atualizando de uma versão anterior?** A feature de cadastro e login mudou
> a tabela `usuarios` sem script de migração. Apague
> `server/database/db.sqlite3` antes de subir a aplicação; o banco é recriado
> automaticamente.

### Autenticação e envio de e-mail

O cadastro exige e-mail institucional (`@puc-rio.br` ou `@aluno.puc-rio.br`)
e só é concluído pelo link de confirmação enviado por e-mail. O login devolve
um token que o front-end envia em `Authorization: Bearer <token>`. As rotas
ficam em `/auth/*` e estão documentadas em http://127.0.0.1:5000/openapi.

| Variável | Padrão | Uso |
|---|---|---|
| `EMAIL_BACKEND` | `log` | `log` (escreve o e-mail no log da aplicação) ou `smtp` |
| `SMTP_HOST`, `SMTP_PORT`, `SMTP_USUARIO`, `SMTP_SENHA` | — | Obrigatórias com `EMAIL_BACKEND=smtp` (conexão com STARTTLS) |
| `EMAIL_REMETENTE` | — | Endereço "De:"; obrigatória com `smtp` |
| `CONFIRMACAO_URL_BASE` | `http://localhost:5173/confirmar-email` | Página do front-end que recebe `?token=` e chama `POST /auth/confirmacao` |
| `SESSAO_DURACAO_HORAS` | `8` | Validade da sessão após o login |

Com `EMAIL_BACKEND=smtp`, a aplicação não sobe se faltar alguma das variáveis
obrigatórias. Segredos SMTP entram só por variável de ambiente, nunca no
repositório.

Em desenvolvimento (backend `log`), o e-mail de confirmação aparece no
terminal do `flask run`, com o link `...?token=<token>`. Para confirmar sem
front-end, envie o token direto à API:

```bash
curl -X POST http://127.0.0.1:5000/auth/confirmacao \
  -H "Content-Type: application/json" -d '{"token": "<token>"}'
```

### Interface web (`front/`)

HTML, CSS e JavaScript puros, sem build nem dependências de npm. Com a API
rodando e `CORS_ORIGINS=http://localhost:5173`:

```bash
make front        # servidor em http://localhost:5173
make front-test   # testes do front (Node 18 ou mais novo)
```

Telas: `/entrar/`, `/cadastro/`, `/confirmar-email/` e `/inicio/`. O endereço da
API fica em `front/js/config.js`. O visual comum está em `front/css/tema.css`,
com demonstração em `/guia-de-estilo/`: use as variáveis e classes do tema
antes de criar estilos novos. Quando o backend for usado por outras pessoas,
`CONFIRMACAO_URL_BASE` precisa apontar para o front publicado.

Para executar os testes:

```bash
make test
```

## Qualidade do código

Use o `Makefile` para executar o lint e/ou todas as verificações:

```bash
make lint
make check
```

`make check` é o alvo padrão e executa lint e testes. O Flake8 segue as regras
em `setup.cfg`. Para gerar cobertura:

```bash
python -m pytest --cov=server.core --cov-report=term-missing
```

## Desenvolvimento guiado por especificações

Toda funcionalidade começa por uma especificação em `spec/features/`.
O fluxo (especificar → planejar → quebrar em tarefas → implementar → validar)
está descrito em [spec/README.md](spec/README.md), e os princípios do projeto
estão em [spec/constitution.md](spec/constitution.md).

## Requisitos do trabalho

- [ ] Pelo menos 4 histórias de usuário implementadas
- [ ] Pelo menos 2 entidades
- [ ] Organização segundo a Clean Architecture
- [ ] Princípios SOLID aplicados
- [ ] Testes unitários dos use cases, isolados da infraestrutura
- [ ] Código seguindo a PEP-8
- [ ] (Bônus) Uso de IA justificado e com boa estratégia
