---
name: implementar-feature-classificados
description: "Use when asked to implement an approved feature or task in the classificados PUC project step by step, following ROTEIRO.md and Clean Architecture. Not for creating SDD artifacts or handling a standalone database-modeling request."
---

# Implementar feature de classificados

Implemente tarefas aprovadas da plataforma de classificados PUC seguindo o
roteiro do repositório, a Clean Architecture e o fluxo de testes. Esta skill
executa implementação; não inventa requisitos, não aprova specs e não substitui
as skills especializadas de SDD, Jira ou modelagem de dados.

## Fontes de verdade

Antes de editar:

- Leia `ROTEIRO.md` para seguir a sequência de trabalho e os limites por camada.
- Leia `ARQUITETURA.md` e `spec/constitution.md` para arquitetura e princípios.
- Leia `spec/features/<feature>/spec.md`, `plan.md` e `tasks.md` para escopo,
  critérios de aceitação e ordem das tarefas.
- Inspecione os módulos e testes existentes relacionados à tarefa.
- Confira `git status` e os diffs staged/unstaged. Preserve alterações do
  usuário e não misture trabalho que não pertence à tarefa.

Jira pode esclarecer requisitos se o usuário pedir ou se a spec depender de
uma confirmação. Não atualize issues nem mude seu estado sem pedido explícito.

## Pré-condições

1. A spec da feature deve estar aprovada e os critérios de aceitação devem
   estar definidos.
2. A tarefa deve existir em `tasks.md` ou ter sido delimitada claramente pelo
   usuário.
3. Decisões de negócio necessárias à tarefa devem estar resolvidas.
4. As dependências da tarefa precisam estar concluídas ou autorizadas no
   escopo informado pelo usuário.

Se uma pré-condição faltar, não implemente por suposição. Explique o bloqueio
e, quando for necessário criar ou revisar os artefatos SDD, use
`criar-feature-sdd`. Pergunte ao usuário quando uma regra de negócio continuar
ambígua.

## Fluxo de implementação

1. Selecione a menor tarefa incompleta compatível com o pedido e confirme sua
   relação com os critérios de aceitação.
2. Escolha os testes que demonstram o comportamento. Escreva ou atualize os
   testes focados antes do código de produção.
3. Implemente somente o necessário para satisfazer a tarefa, seguindo as
   responsabilidades da arquitetura:
   - `server/core/entities/`: entidades e regras puras, sem frameworks;
   - `server/core/interfaces/`: contratos mínimos consumidos pelo core;
   - `server/core/usecases/`: ações de negócio dependentes de abstrações;
   - `server/infra/`: persistência e integrações;
   - `server/api/presenters/`: representação de saída;
   - `server/api/controllers/`: entrada HTTP e tradução na fronteira;
   - `server/app.py`: composição das dependências concretas.
4. Teste regras do core com dependências em memória. Teste gateways com banco
   de teste e controllers pelos contratos HTTP, conforme o comportamento.
5. Atualize documentação diretamente relacionada quando o comportamento,
   configuração, arquitetura ou persistência mudar.
6. Revise o diff para confirmar que não alterou requisitos, arquivos ou
   camadas fora do escopo.

Implemente uma tarefa ou fatia vertical por vez. Não reescreva a aplicação
inteira quando o pedido cobrir uma tarefa específica.

## Persistência e skills relacionadas

Se a tarefa adicionar, alterar ou remover entidades, tabelas, colunas, campos,
constraints, relacionamentos ou formatos persistidos, siga a skill
`manter-modelagem-dados`. Mantenha sincronizados:

- modelos SQLAlchemy e `server/infra/db/schema.sql`;
- inicialização ou migrações;
- `server/infra/db/README.md`;
- testes de persistência e constraints.

Preserve dados existentes. Não trate `create_all` como migração. Mudanças
destrutivas ou regras de transformação indefinidas exigem confirmação do
usuário.

Se ainda for necessário criar ou alterar `spec.md`, `plan.md` ou `tasks.md`,
use `criar-feature-sdd`; não replique seu fluxo aqui. Use as skills Jira quando
o pedido envolver consulta ou alteração de issues.

## Validação

- Execute primeiro os testes focados na mudança.
- Rode `make check` quando viável para validar Flake8 e a suíte de testes.
- Confirme cada critério de aceitação afetado; não use somente lint ou build
  como substituto para teste de comportamento.
- Se um comando falhar por causa de ambiente ou dependências, reporte a falha
  e a evidência; não apresente a implementação como validada.
- Não corrija problemas preexistentes fora do escopo, a menos que impeçam a
  tarefa ou tenham sido causados por ela.

## Limites e interrupções

Pare e consulte o usuário quando:

- a spec estiver em rascunho ou houver regra de negócio pendente;
- o contrato público precisar de uma escolha não aprovada;
- uma migração puder perder ou transformar dados sem regra definida;
- alterações staged/unstaged conflitarem com a tarefa;
- a implementação exigir ampliar o escopo ou mudar a arquitetura.

Não:

- crie requisitos, campos, endpoints ou dependências por conveniência;
- deixe detalhes de Flask ou SQLAlchemy vazarem para o core;
- silencie erros ou use respostas de sucesso como fallback;
- altere arquivos de referência anexados em modo somente leitura;
- stageie arquivos, crie commits ou faça push sem pedido explícito.

Se o usuário pedir commits, apresente primeiro a divisão proposta, seus
arquivos e a sequência passo a passo; só então crie os commits autorizados.

## Resposta

Informe a tarefa implementada, os arquivos alterados, os testes executados e
seus resultados. Liste critérios ou decisões ainda pendentes e deixe claro
qualquer validação que não pôde ser concluída.
