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

1. **Especificar**: crie `features/NNN-nome/` e copie `templates/spec-template.md`
   para `spec.md`. Descreva a história de usuário e os critérios de aceitação,
   sem falar de tecnologia.
2. **Planejar**: copie `plan-template.md` para `plan.md`. Defina entidades,
   use cases, repositórios e rotas, respeitando a `constitution.md`.
3. **Quebrar em tarefas**: copie `tasks-template.md` para `tasks.md` e liste
   as tarefas em ordem (testes primeiro).
4. **Implementar**: execute as tarefas, marcando cada uma como concluída.
5. **Validar**: confira se todos os critérios de aceitação da `spec.md` têm
   teste passando.

Numere as features em sequência (`001`, `002`, ...). O trabalho exige
**pelo menos 4 histórias de usuário** e **pelo menos 2 entidades**.
