---
name: criar-feature-sdd
description: "Use when the user asks to start a new feature, create SDD artifacts, or turn a product request into a specification, technical plan, and implementation tasks for this project."
---

# Criar Feature com SDD

Crie os artefatos de uma feature seguindo o fluxo Spec-Driven Development
deste repositório. Esta skill prepara a feature; ela não implementa código.

## Fontes de verdade

Antes de criar os arquivos, consulte:

- `spec/README.md` para o fluxo e a estrutura do SDD.
- `spec/constitution.md` para as regras obrigatórias de arquitetura, código e
  testes.
- `spec/templates/spec-template.md`, `spec/templates/plan-template.md` e
  `spec/templates/tasks-template.md` para os formatos dos artefatos.
- As features existentes em `spec/features/` para evitar IDs repetidos e
  manter consistência com o projeto.

## Fluxo

1. Entenda o objetivo, os usuários envolvidos, o benefício esperado e os
   critérios de aceitação. Faça perguntas objetivas quando faltarem decisões
   necessárias; não invente regras de negócio.
2. Determine o próximo ID sequencial de três dígitos com base nas pastas de
   `spec/features/`. Use o formato `NNN-nome-curto-em-kebab-case`.
3. Crie `spec/features/NNN-nome/` com `spec.md`, `plan.md` e `tasks.md`, usando
   os templates do projeto como estrutura.
4. Escreva a spec em linguagem de produto, sem decisões de tecnologia nos
   critérios de aceitação. Registre regras de negócio, itens fora de escopo e
   dúvidas em aberto. Inicie o status como `Rascunho`; só marque `Aprovada`
   quando o usuário confirmar explicitamente.
5. Elabore o plano técnico a partir da spec e respeite a constituição. Mantenha
   as regras de negócio em `domain/` e `use_cases/`, detalhes de HTTP em
   `app/`, detalhes de persistência e integrações em `infra/`, e dependências
   apontando para dentro.
6. Divida o trabalho em tarefas pequenas e ordenadas, escrevendo testes antes
   da implementação. Inclua validação dos critérios de aceitação, `pytest` e
   `flake8` quando aplicáveis.
7. Confira que os três documentos concordam entre si, que nenhuma decisão
   pendente foi apresentada como certa e que não há código de aplicação sendo
   implementado como parte desta skill.

## Resposta

Ao terminar, informe o ID e os caminhos dos artefatos criados, resuma as
principais decisões e liste as dúvidas ainda abertas. Se não foi possível
definir algum ponto sem inventar comportamento, deixe-o registrado na spec e
explique isso ao usuário.