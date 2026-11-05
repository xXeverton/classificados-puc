# Constituição do Projeto

Princípios que toda especificação, plano e implementação devem seguir.

## 1. Clean Architecture

As dependências apontam sempre para dentro:

```
app/ (Flask, rotas)  →  use_cases/  →  domain/
infra/ (SQLite, repositórios)  →  use_cases/ (interfaces)  →  domain/
```

- `domain/`: entidades e regras de negócio puras. Não importa Flask, SQLite
  nem nada de fora.
- `use_cases/`: orquestra as regras de negócio. Depende apenas de `domain/`
  e de **interfaces** (abstrações) de repositório.
- `infra/`: implementações concretas (repositórios SQLite, conexão com o banco).
- `app/`: camada web (Flask). Converte HTTP em chamadas aos use cases.

## 2. SOLID

- **S**: cada classe tem uma única responsabilidade (um use case por ação).
- **O**: novas funcionalidades entram por extensão, não alterando código estável.
- **L**: qualquer implementação de repositório substitui a interface sem quebrar.
- **I**: interfaces pequenas e específicas.
- **D**: use cases recebem os repositórios por injeção de dependência.

## 3. Testes

- Todo use case tem testes unitários com `pytest`.
- Os testes de use cases usam repositórios falsos (em memória), nunca o banco.
- Cada critério de aceitação da spec corresponde a pelo menos um teste.

## 4. Estilo

- Código segue a PEP-8 (verificado com `flake8`).
- Nomes de classes, funções e variáveis devem ser descritivos.

## 5. Uso de IA

- A IA é usada a partir das specs desta pasta, nunca sem contexto.
- Todo código gerado é revisado e testado antes de ser incorporado.
