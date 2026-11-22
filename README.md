# Projeto de Engenharia de Software

API web em **Python + Flask-OpenAPI3** construída com **Clean Architecture**,
**SQLAlchemy + SQLite**, princípios **SOLID**, testes unitários com **pytest**
e desenvolvimento guiado por especificações (**Spec-Driven Development**).

> Trabalho 2 de Engenharia de Software: Arquitetura e Projeto de Software (PUC-Rio).

## Estrutura do projeto

A organização das camadas e o mapa de diretórios estão em
[ARQUITETURA.md](ARQUITETURA.md). O código da API fica em `server/`; as
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

## Executar

```bash
make backend   # API em http://127.0.0.1:5000
make front     # front em http://localhost:5173
```

Variáveis de ambiente, autenticação, e-mail e fotos estão em
[server/README.md](server/README.md); as telas, em
[front/README.md](front/README.md).

## Testes

```bash
make test         # API (pytest)
make front-test   # front (Node 18 ou mais novo)
make check        # lint + testes do backend + testes do front
```

## Qualidade do código

Use o `Makefile` para executar o lint e/ou todas as verificações:

```bash
make lint
make check
```

`make check` é o alvo padrão e executa todas as verificações automatizadas.
O Flake8 segue as regras em `setup.cfg`. Para gerar cobertura:

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
