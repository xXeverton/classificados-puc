# Estrutura do projeto

## Camadas

- `app/`: aplicação Flask e adaptadores HTTP.
- `domain/`: entidades e regras de negócio sem dependências externas.
- `use_cases/`: casos de uso e orquestração.
- `infra/`: persistência e integrações concretas.
- `tests/`: testes organizados por camada.
- `spec/`: especificações, planos e tarefas do fluxo SDD.
- `.github/skills/`: fluxos especializados para o agente.

As dependências de código apontam para dentro: `app` e `infra` dependem de
`use_cases`, que depende de `domain`.

## Mapa de diretórios

```text
classificados-puc/
├── .github/skills/            # Skills do projeto
├── app/
│   ├── routes/                # Blueprints e rotas HTTP
│   └── main.py                # App factory
├── domain/                    # Entidades e regras de negócio
├── infra/
│   ├── db/                    # Schema e inicialização SQLite
│   └── repositories/          # Repositórios concretos
├── spec/
│   ├── features/              # Specs por feature
│   └── templates/             # Templates de spec, plano e tarefas
├── tests/
│   ├── domain/
│   ├── infra/
│   └── use_cases/
├── use_cases/                 # Casos de uso
├── Makefile                   # Instalação, lint e testes
├── README.md                  # Guia principal
├── requirements.txt           # Dependências Python
└── setup.cfg                  # Configuração de pytest e Flake8
```
