---
name: criar-subtask-jira
description: "Use when asked to create or break down work into Jira subtasks. Inspect sibling subtasks and the parent issue first, then follow this project's `[Area]: <ação objetiva>` summary convention."
---

# Criar Subtask no Jira

Crie subtasks no Jira deste projeto seguindo os padrões reais das subtasks
existentes. Esta skill cria issues apenas quando o usuário solicitar
explicitamente.

## Procedimento

1. Identifique a chave do projeto e a issue pai. Se alguma delas não estiver
   clara, pergunte; não escolha um projeto ou pai por suposição.
2. Use ferramentas Jira de leitura para consultar a issue pai e subtasks irmãs.
   Confira o tipo da issue pai, o contexto, as áreas usadas nos títulos e se as
   subtasks existentes têm descrição ou são definidas somente pelo resumo.
3. Divida o escopo em unidades pequenas, implementáveis e verificáveis.
   Cada subtask deve representar uma entrega coesa, sem duplicar o trabalho de
   outra subtask ou da issue pai.
4. Formate o resumo no padrão observado no projeto:
   `[Área]: <ação objetiva e resultado esperado>`.
   Exemplos de áreas existentes incluem `[Back-end]`, `[Front-end]`,
   `[Database]` e `[Infra/Storage]`. Use a área adequada ao trabalho, mantendo
   capitalização e pontuação consistentes.
5. Siga o padrão de descrição da issue pai e das subtasks irmãs. No projeto,
   subtasks podem não ter descrição; não invente detalhes, critérios ou
   decisões técnicas ausentes. Se mais contexto for necessário, inclua somente
   os requisitos fornecidos ou confirmados pelo usuário.
6. Antes de escrever no Jira, apresente ao usuário a issue pai, os resumos,
   descrições propostas e responsáveis (se aplicável) e peça confirmação
   explícita. Não crie subtasks a partir de uma sugestão sem confirmação.
7. Após confirmação, use a ferramenta Jira de criação disponível. Defina o tipo
   exato `Subtask` e a issue pai. Se a ferramenta disponível não suportar a
   criação de subtasks ou não aceitar esse tipo, pare e informe o bloqueio; não
   crie uma Task/Story como substituta.
8. Verifique as issues criadas com uma consulta de leitura e informe chaves,
   resumos, pais, status e links. Se a criação falhar parcialmente, informe
   exatamente quais foram criadas e quais não foram.

## Restrições

- Nunca altere ou crie issues sem pedido explícito e confirmação do conteúdo.
- Não atribua responsáveis nem defina estimativas, prioridade, sprint ou status
  sem instrução do usuário.
- Não afirme que uma subtask foi criada sem confirmar o resultado retornado pelo
  Jira.
