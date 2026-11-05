# Projeto de Engenharia de Software

Aplicação web em **Python + Flask** construída com **Clean Architecture**,
princípios **SOLID**, testes unitários com **pytest** e desenvolvimento
guiado por especificações (**Spec-Driven Development**).

> Trabalho 2 de Engenharia de Software: Arquitetura e Projeto de Software (PUC-Rio).

## Estrutura do projeto

```
projeto_engenharia_de_software/
├── app/                    # Frameworks & Drivers: Flask
│   ├── routes/             # Blueprints / rotas HTTP
│   └── main.py             # App factory (create_app)
├── domain/                 # Entidades e regras de negócio puras
├── use_cases/              # Casos de uso (lógica da aplicação)
├── infra/                  # Implementações concretas
│   ├── repositories/       # Repositórios (ex.: SQLite)
│   └── db/                 # Conexão / configuração do banco
├── tests/                  # Testes unitários (pytest)
│   ├── domain/
│   └── use_cases/
├── spec/                   # Spec-Driven Development (ver spec/README.md)
│   ├── constitution.md     # Princípios do projeto
│   ├── templates/          # Modelos de spec, plano e tarefas
│   └── features/           # Uma pasta por história de usuário
├── requirements.txt        # Dependências
├── setup.cfg               # Configuração do flake8 e pytest
└── README.md
```

As dependências apontam para dentro: `app` e `infra` dependem de `use_cases`,
que dependem de `domain`. O `domain` não depende de nada externo.

## Pré-requisitos

- Python 3.11 ou superior
- Git

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
pip install -r requirements.txt
```

## Executar a aplicação

```bash
flask --app app.main:create_app run --debug
```

A aplicação sobe em http://127.0.0.1:5000. Para conferir, acesse
http://127.0.0.1:5000/health, que deve responder `{"status": "ok"}`.

## Executar os testes

```bash
pytest
```

Com relatório de cobertura:

```bash
pytest --cov=domain --cov=use_cases --cov-report=term-missing
```

## Verificar o estilo (PEP-8)

```bash
flake8
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
