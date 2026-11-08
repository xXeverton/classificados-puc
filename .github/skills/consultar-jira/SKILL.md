---
name: consultar-jira
description: "Use when the user asks to find, list, filter, or inspect Subtasks in the project's Jira. Requires the Atlassian Jira MCP server to be connected and authorized."
---

# Consultar Jira

Use the connected Atlassian MCP server to answer read-only questions about
Jira Subtasks for this project.

## Regras

- Use somente ferramentas Jira de leitura, como pesquisar issues e consultar
  detalhes. Não crie, edite, transicione ou exclua issues.
- Consulte apenas o tipo de issue `Subtask`, salvo se o usuário pedir
  explicitamente outros tipos.
- Se o projeto Jira não estiver claro, pergunte a chave do projeto. Não escolha
  um projeto por suposição.
- Converta filtros solicitados pelo usuário em uma consulta Jira apropriada.
  Respeite todos os filtros, como status, responsável, sprint e período.
- Para listagens extensas, use paginação e informe se os resultados exibidos
  são parciais. Não afirme que a lista está completa sem verificar isso.
- Resuma cada resultado com chave, título, tipo, status, responsável e link
  quando esses dados estiverem disponíveis. Inclua outros campos apenas se
  forem relevantes à pergunta.
- Se a conexão, autenticação ou permissão falhar, informe o bloqueio e não
  invente resultados. Não peça que o usuário envie tokens ou senhas pelo chat.
- Quando o usuário pedir listagens em projetos com Storys ou Tasks, mas a intenção
  for focar em subtasks, priorize o filtro por `Subtask` e mantenha a resposta
  alinhada a esse escopo.

## Resposta

Responda em português, a menos que o usuário peça outro idioma. Para listas,
use uma tabela concisa. Ao final, indique os filtros usados e eventuais limites
ou dados indisponíveis.