# Spec-Driven Development (SDD)

Esta pasta guarda as especificações que guiam o desenvolvimento. A regra é
simples: **nenhum código é escrito sem uma especificação aprovada antes**.
As specs também servem de contexto para o uso de IA no projeto (bônus do
trabalho), deixando registrado o que foi pedido e por quê.

## Estrutura

```
spec/
├── README.md            # Este arquivo: como usar o SDD no projeto
├── constitution.md      # Princípios inegociáveis do projeto
├── decisoes.md          # Registro de decisões gerais (produto e técnicas)
├── templates/           # Modelos para copiar ao criar uma nova feature
│   ├── spec-template.md   # O QUÊ e POR QUÊ (histórias de usuário)
│   ├── plan-template.md   # COMO (decisões técnicas por camada)
│   └── tasks-template.md  # Passos de implementação
└── features/            # Uma pasta por feature/história de usuário
    └── 001-nome-da-feature/
        ├── spec.md
        ├── plan.md
        └── tasks.md
```

## Fluxo de trabalho

0. **Consultar as decisões**: leia [`decisoes.md`](decisoes.md) antes de
   especificar. O que já está decidido lá não é perguntado de novo; a spec
   cita o ID da decisão (`D-NNN`).
1. **Especificar**: crie `features/NNN-nome/` e copie `templates/spec-template.md`
   para `spec.md`. Descreva a história de usuário e os critérios de aceitação,
   sem falar de tecnologia.
2. **Planejar**: copie `plan-template.md` para `plan.md`. Defina entidades,
   use cases, repositórios e rotas, respeitando a `constitution.md`.
3. **Quebrar em tarefas**: copie `tasks-template.md` para `tasks.md` e liste
   as tarefas em ordem (testes primeiro).
4. **Implementar**: execute as tarefas, marcando cada uma como concluída.
   Para features aprovadas, siga o [`ROTEIRO.md`](../ROTEIRO.md) e a skill
   [`implementar-feature-classificados`](../.github/skills/implementar-feature-classificados/SKILL.md).
5. **Validar**: confira se todos os critérios de aceitação da `spec.md` têm
   teste passando.

Quando uma dúvida de uma spec for respondida e a resposta valer para o projeto
inteiro, registre-a também em `decisoes.md`.

Numere as features em sequência (`001`, `002`, ...). O trabalho exige
**pelo menos 4 histórias de usuário** e **pelo menos 2 entidades**.

## Skills e especificações

`spec/` contém os requisitos e artefatos do produto: specs, planos, tarefas,
templates e a constituição. As skills são instruções de fluxo de trabalho para
o Copilot e ficam em `.github/skills/`; mantenha cada artefato no seu local,
sem duplicar as instruções das skills dentro das specs.

- [`criar-feature-sdd`](../.github/skills/criar-feature-sdd/SKILL.md) cria
  `spec.md`, `plan.md` e `tasks.md`.
- [`implementar-feature-classificados`](../.github/skills/implementar-feature-classificados/SKILL.md)
  implementa tarefas de uma feature aprovada, seguindo o roteiro do projeto.
- [`manter-modelagem-dados`](../.github/skills/manter-modelagem-dados/SKILL.md)
  mantém modelo, schema, documentação e testes sincronizados quando dados
  persistidos mudam.
- [`consultar-jira`](../.github/skills/consultar-jira/SKILL.md) e
  [`criar-subtask-jira`](../.github/skills/criar-subtask-jira/SKILL.md)
  orientam os fluxos correspondentes de Jira.
