# Tarefas: Utilitário para gerar link de contato do WhatsApp

Referências: `spec.md` e `plan.md` desta pasta; Jira PROJ-50.
Marque `[x]` ao concluir. Escreva os testes antes da implementação.

Status atual: **Rascunho**. Resolver as dúvidas em aberto e aprovar a spec
antes de implementar, conforme D-051.

## Contrato e testes

- [ ] T1: Confirmar com o PO o conteúdo da mensagem e resolver os casos de
  números internacionais, título vazio e limites de tamanho.
- [ ] T2: Escrever testes de unidade em `front/tests/` para normalização,
  código de país, números inválidos, codificação da mensagem e uso dos dados
  recebidos em cada chamada.

## Implementação

- [ ] T3: Implementar a função pura de geração de link em
  `front/js/dominio/`, sem integração visual ou estado global.
- [ ] T4: Executar os testes do front e conferir cada critério de aceitação
  aprovado.

## Validação

- [ ] T5: `make front-test` passa.
- [ ] T6: Critérios de aceitação aprovados estão cobertos por testes.
