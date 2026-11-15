# Roteiro para criar o projeto do zero

Este roteiro organiza, em ordem, como iniciar e desenvolver a plataforma de
classificados da comunidade PUC. Ele combina as decisões registradas no
projeto, o fluxo Spec-Driven Development (SDD) e os prompts usados nas
conversas para adaptar a arquitetura de referência ao nosso domínio.

O documento é um guia para um início do zero; antes de executar qualquer
passo, confira o estado atual do repositório para não recriar o que já existe.

## 1. Entender o problema e confirmar as regras

- Identificar os usuários, suas necessidades e o benefício de cada história.
- Consultar no Jira a épica e as histórias relacionadas ao cadastro,
  autenticação e perfil. As conversas anteriores usaram `PROJ-8`, `PROJ-1` e
  `PROJ-4` como referência.
- Separar regras confirmadas de decisões pendentes. Não transformar hipótese
  em requisito.
- Confirmar, antes de implementar autenticação:
  - se o login será por matrícula ou e-mail institucional (a escolha depende
    do resultado do EN01);
  - quais vínculos podem criar conta;
  - quais dados do perfil serão visíveis para compradores;
  - quais formatos de imagem serão aceitos.
- Registrar as regras confirmadas na especificação. Entre as regras já
  discutidas estão a elegibilidade de alunos e funcionários, a proteção de
  senhas, o perfil completo para publicar e o bloqueio temporário após
  tentativas inválidas. Validar sempre esses detalhes com a fonte atual no
  Jira antes de codificá-los.

**Saída desta etapa:** lista de histórias, critérios de aceitação e decisões
em aberto, sem escolhas técnicas misturadas aos requisitos de produto.

## 2. Definir a arquitetura para o domínio

- Usar a arquitetura de referência fornecida como base de organização, não
  como definição das entidades ou funcionalidades do produto.
- Adaptar essa referência ao domínio de classificados e registrar o resultado
  em [`ARQUITETURA.md`](./ARQUITETURA.md), respeitando as regras confirmadas
  no Jira.
- Manter as dependências apontando para dentro:
  - `server/core/entities/`: entidades e regras de negócio puras;
  - `server/core/usecases/`: ações de negócio;
  - `server/core/interfaces/`: contratos usados pelo core;
  - `server/infra/`: persistência e integrações;
  - `server/api/controllers/`: entrada HTTP;
  - `server/api/presenters/`: representação das respostas;
  - `server/app.py`: composição da aplicação e injeção de dependências.
- Diferenciar claramente o que é arquitetura-alvo e o que já está
  implementado. Não documentar módulos futuros como se já existissem.

**Saída desta etapa:** mapa de camadas e responsabilidades revisado para o
domínio, antes de planejar a implementação.

## 3. Especificar cada funcionalidade com SDD

Para cada história:

1. Criar uma pasta numerada em `spec/features/`, seguindo
   [`spec/README.md`](./spec/README.md).
2. Escrever `spec.md` a partir de uma história de usuário, regras de negócio,
   critérios de aceitação e itens fora de escopo.
3. Marcar decisões não resolvidas como pendentes e perguntar ao responsável;
   não inventar respostas.
4. Manter a spec em rascunho até a aprovação explícita.
5. Escrever `plan.md` com entidades, casos de uso, interfaces, persistência,
   endpoints e estratégia de testes, em conformidade com
   [`spec/constitution.md`](./spec/constitution.md).
6. Escrever `tasks.md` em passos pequenos, ordenados e verificáveis; planejar
   os testes antes da implementação.
7. Conferir se spec, plano e tarefas concordam entre si e se cada critério de
   aceitação tem uma tarefa e uma forma de validação.

O trabalho acadêmico registra como metas pelo menos quatro histórias de
usuário e duas entidades. Planejar como metas do produto, sem criar histórias
artificiais apenas para atingir a contagem.

## 4. Criar a base técnica do repositório

- Preparar Python 3.11 ou superior, Git e GNU Make.
- Criar o ambiente virtual e instalar as dependências pelo `Makefile`.
- Separar as dependências da aplicação e as ferramentas de teste/lint em
  `server/requirements.txt`.
- Configurar Flask-OpenAPI3 para HTTP, SQLAlchemy sobre SQLite para
  persistência, pytest para testes e Flake8 para estilo.
- Criar a estrutura inicial em `server/`, `tests/` e `spec/`.
- Configurar `make install`, `make lint`, `make test` e `make check`.
- Criar a aplicação mínima e preservar `GET /health` como verificação de
  inicialização.
- Manter configurações variáveis por ambiente, como `DATABASE_URL` e
  `CORS_ORIGINS`, fora das regras de negócio.

**Saída desta etapa:** projeto inicializável, dependências instaláveis e
validações automatizadas executáveis.

## 5. Modelar persistência com cuidado

- Definir primeiro as entidades e regras no core; não usar o modelo ORM como
  entidade de domínio.
- Para cada dado persistido, atualizar em conjunto:
  1. modelo SQLAlchemy e schema SQLite;
  2. inicialização do banco ou migração necessária;
  3. documentação em `server/infra/db/README.md`;
  4. testes de constraints e comportamento.
- Preservar dados existentes. `create_all` cria tabelas ausentes, mas não
  modifica tabelas já existentes; alterações incompatíveis exigem migração
  explícita.
- Não acrescentar campos de autenticação ou perfil ao banco até as regras e
  necessidades de migração estarem definidas.

**Saída desta etapa:** modelo persistido documentado, com testes e plano de
evolução de dados.

## 6. Implementar cada história de dentro para fora

Para cada feature aprovada, seguir a ordem abaixo e os limites da
[`constituição`](./spec/constitution.md):

1. **Entidades:** implementar regras puras no core e testar sucesso e falha.
2. **Interfaces:** definir contratos pequenos, específicos e consumidos pelos
   casos de uso.
3. **Casos de uso:** implementar uma ação de negócio por vez, injetando
   interfaces em vez de criar infraestrutura concreta.
4. **Testes unitários:** usar repositórios falsos em memória para manter os
   casos de uso independentes do banco.
5. **Gateways:** implementar interfaces na infraestrutura; testar persistência
   e tradução entre modelos ORM e entidades.
6. **Controllers:** validar a estrutura HTTP, chamar o caso de uso e não
   concentrar regras de negócio na rota.
7. **Presenters:** converter resultados e erros em respostas HTTP; manter
   detalhes de HTTP fora do core.
8. **Composição:** conectar dependências em `server/app.py`.
9. **Integração:** validar o comportamento ponta a ponta e os critérios de
   aceitação da spec.

Trabalhar em fatias verticais pequenas. Por exemplo, completar uma história
com seus testes e endpoint antes de começar várias funcionalidades sem
integração.

## 7. Validar e revisar continuamente

- Executar primeiro os testes focados na funcionalidade e, em seguida,
  `make check`.
- Conferir que cada critério de aceitação foi exercitado por testes.
- Revisar erros, segurança e exposição de dados pessoais, especialmente em
  autenticação e respostas de perfil.
- Conferir documentação, schema, modelos e código juntos quando uma mudança
  tocar persistência ou arquitetura.
- Não considerar testes passando como prova de requisitos que ainda não foram
  definidos.
- Registrar decisões pendentes e evidências da validação.

## 8. Preparar entregas e commits

- Revisar o diff e o estado do Git antes de stagear.
- Agrupar mudanças relacionadas em commits pequenos e coerentes, mantendo
  implementação, testes e documentação necessária juntos.
- Antes de criar commits, explicar o conteúdo e a sequência de cada commit,
  passo a passo.
- Não incluir arquivos de referência ou rascunhos só por estarem no
  repositório; confirmar se fazem parte da entrega.
- Após os commits, verificar o histórico, o status do working tree e os
  resultados das validações.

## Prompts que orientaram este roteiro

As conversas anteriores usaram estes pedidos para definir a sequência de
trabalho:

1. “Vamos ajustar para o nosso domínio. Utilize como base o
   `ARQUITETURA.md` para ajustar o `ESTRUTURA.md` conforme nossas regras de
   domínio do Jira.”
2. “Agora o MCP do Jira está conectado. Revise novamente.”
3. “Siga a arquitetura de `ARQUITETURA.md` para adaptar a arquitetura de
   `ESTRUTURA.md`. Vá perguntando passo a passo caso tenha dúvida.”
4. “Reestruture a partir da estrutura de pastas um Markdown. Use como base o
   `ARQUITETURA.md`.”
5. “Siga à risca o `ARQUITETURA.md`.”

Em conjunto, esses prompts estabelecem a ordem central do projeto:
**entender e confirmar o domínio → adaptar a arquitetura → especificar →
planejar → implementar em camadas → validar**. O conteúdo de referência deve
ser adaptado ao projeto, não copiado como se descrevesse automaticamente
nosso domínio.
