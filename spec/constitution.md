# Constituição do Projeto

Princípios que toda especificação, plano e implementação devem seguir.

## 1. Clean Architecture

As dependências de código apontam sempre para dentro. Camadas internas não
conhecem nem importam detalhes das camadas externas:

```
app/ (Flask, rotas)  →  use_cases/  →  domain/
infra/ (SQLite, repositórios)  →  interfaces definidas em use_cases/  →  domain/
```

- `domain/`: entidades, objetos de valor e regras de negócio puras. Não importa
  Flask, SQLite, bibliotecas de infraestrutura nem outras camadas externas.
- `use_cases/`: coordena uma ação de negócio por caso de uso. Depende do domínio
  e de abstrações necessárias, nunca de implementações concretas.
- `infra/`: implementa persistência e integrações externas, incluindo os
  repositórios concretos que cumprem as interfaces internas.
- `app/`: adaptador de entrada HTTP. Converte requisições em chamadas aos casos
  de uso e seus resultados em respostas HTTP; não contém regras de negócio.
- A montagem das dependências acontece na inicialização da aplicação. Os casos
  de uso recebem suas dependências por parâmetro, sem criar conexões ou
  repositórios concretos por conta própria.
- Dados e erros são traduzidos nas fronteiras entre camadas. Detalhes de HTTP,
  SQL e Flask não vazam para o domínio nem para os casos de uso.
- Novas integrações externas são acessadas por abstrações consumidas pela
  camada interna e implementadas em `infra/`.

## 2. Clean Code

- Use nomes claros e específicos para variáveis, funções, classes e módulos;
  evite abreviações obscuras e nomes que escondam intenção.
- Cada função deve ter um propósito coeso, executar uma tarefa e manter efeitos
  colaterais explícitos. Prefira parâmetros e retornos simples.
- Mantenha funções e módulos pequenos o bastante para que sua responsabilidade
  seja fácil de entender. Extraia código quando isso melhorar a coesão ou
  remover duplicação real, sem criar abstrações especulativas.
- Evite números e strings mágicos: dê nomes a valores de negócio relevantes e
  centralize configurações que variam por ambiente.
- Trate erros de forma explícita e consistente. Não silencie exceções nem use
  valores de retorno ambíguos para representar falhas.
- Comentários devem explicar decisões ou restrições que não sejam evidentes no
  código; não devem repetir o que o código já expressa.
- Prefira código simples e direto a otimizações prematuras. Preserve a
  compatibilidade das interfaces públicas ao evoluir uma funcionalidade.

## 3. SOLID

- **S**: cada classe tem uma única responsabilidade (um use case por ação).
- **O**: novas funcionalidades entram por extensão, não alterando código estável.
- **L**: qualquer implementação de repositório substitui a interface sem quebrar.
- **I**: interfaces pequenas e específicas.
- **D**: use cases recebem os repositórios por injeção de dependência.

## 4. Testes

- Todo use case tem testes unitários com `pytest`.
- Os testes de use cases usam repositórios falsos (em memória), nunca o banco.
- Testes devem verificar comportamento observável, com nomes que indiquem o
  cenário e o resultado esperado.
- Cada regra de negócio relevante deve ter cobertura de sucesso e de falha.
- Cada critério de aceitação da spec corresponde a pelo menos um teste.

## 5. Estilo

- Código segue a PEP-8 (verificado com `flake8`).
- Nomes de classes, funções e variáveis devem ser descritivos e consistentes.
- Módulos importam apenas o necessário e não introduzem dependências circulares.

## 6. Uso de IA

- A IA é usada a partir das specs desta pasta, nunca sem contexto.
- Todo código gerado é revisado e testado antes de ser incorporado.
