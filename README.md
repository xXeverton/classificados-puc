# Projeto de Engenharia de Software

Aplicação web em **Python + Flask** construída com **Clean Architecture**,
princípios **SOLID**, testes unitários com **pytest** e desenvolvimento
guiado por especificações (**Spec-Driven Development**).

> Trabalho 2 de Engenharia de Software: Arquitetura e Projeto de Software (PUC-Rio).

## Estrutura do projeto

A organização das camadas e o mapa de diretórios estão em
[ESTRUTURA.md](ESTRUTURA.md).

As dependências apontam para dentro: `app` e `infra` dependem de `use_cases`,
que dependem de `domain`. O `domain` não depende de nada externo.

## Modelagem do banco de dados

O schema SQLite e a documentação das tabelas estão em
[infra/db/README.md](infra/db/README.md). Sempre que dados persistidos forem
adicionados, alterados ou removidos, mantenha o schema, a documentação, os
testes e as migrações aplicáveis sincronizados.

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
flask --app app.main:create_app run --debug
```

A aplicação sobe em http://127.0.0.1:5000. Para conferir, acesse
http://127.0.0.1:5000/health, que deve responder `{"status": "ok"}`.

### Variáveis de ambiente

| Variável | Padrão | Uso |
|---|---|---|
| `JWT_SECRET` | temporário (gerado a cada início) | Segredo que assina os tokens de sessão. Obrigatório fora do desenvolvimento |
| `JWT_EXPIRA_MINUTOS` | `60` | Validade do token de sessão |
| `URL_LINK_MAGICO` | `http://localhost:5000/entrar/link` | Endereço do front que recebe `?token=` do link enviado por e-mail |
| `SMTP_HOST` | vazio | Servidor SMTP. Vazio: o e-mail é escrito no log em vez de enviado |
| `SMTP_PORT` | `587` | Porta SMTP |
| `SMTP_USUARIO` / `SMTP_SENHA` | vazio | Credenciais SMTP, se o servidor exigir |
| `SMTP_REMETENTE` | `nao-responda@localhost` | Remetente dos e-mails |
| `SMTP_STARTTLS` | `true` | Usa STARTTLS na conexão SMTP |

As rotas de autenticação (`/auth/...`) estão descritas em
[spec/features/001-autenticacao/plan.md](spec/features/001-autenticacao/plan.md).

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
python -m pytest --cov=domain --cov=use_cases --cov-report=term-missing
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
