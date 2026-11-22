# Roteiro para construir o projeto passo a passo

Este roteiro é um fluxo
de criação para a plataforma de classificados da comunidade PUC.

O fluxo é: **confirmar o domínio → adaptar a arquitetura → especificar →
planejar → implementar em camadas → validar → entregar**.

As fontes de verdade têm responsabilidades diferentes: Jira para regras e
decisões de produto, specs aprovadas para critérios de aceitação,
[`ARQUITETURA.md`](./ARQUITETURA.md) e
[`spec/constitution.md`](./spec/constitution.md) para organização técnica, e
o código/testes para o comportamento já implementado. Este roteiro orienta o
processo; não substitui essas fontes.

> Este roteiro descreve como começar do zero. O repositório já possui uma base
> de API, endpoint de saúde, entidade e persistência de `Usuario`. Antes de
> executar qualquer prompt, confira o estado atual para evitar recriar ou
> sobrescrever arquivos. As partes de autenticação, perfil e anúncios devem
> seguir specs aprovadas; não são presumidas como implementadas.

## 0. Confirmar domínio e escopo

Comece pelas regras de produto e pelas histórias no Jira. As conversas
anteriores consultaram a épica `PROJ-8` e as histórias `PROJ-1` e `PROJ-4`.
Confirme que esses itens continuam sendo a fonte atual antes de usá-los.

1. Identifique atores, objetivos, regras e critérios de aceitação.
2. Separe requisitos confirmados, decisões pendentes e itens fora de escopo.
3. Resolva as decisões necessárias antes de fixá-las no modelo ou no código.
   Entre os pontos já apontados como pendentes estão:
   - matrícula ou e-mail institucional como identificador de login, conforme
     o resultado do EN01;
   - visibilidade dos dados do perfil para compradores;
   - formatos de imagem aceitos.
4. Confirme com a fonte de produto as regras de elegibilidade, bloqueio de
   tentativas, perfil completo e publicação antes de implementá-las.

A validação de domínio do e-mail é diferente da escolha do identificador de
login. A regra atualmente registrada para a entidade aceita
`@aluno.puc-rio.br` e `@puc-rio.br`; isso não resolve, por si só, se a pessoa
entrará com matrícula ou e-mail.

**Prompt**

```text
Revise no Jira a épica e as histórias relacionadas a autenticação, perfil e
anúncios da plataforma de classificados PUC. Para cada história, resuma:
atores, objetivo, regras confirmadas, critérios de aceitação, itens fora de
escopo e decisões pendentes.

Não invente regras nem escolha entre alternativas em aberto. Destaque o que
precisa de confirmação antes de criar entidades, campos persistidos ou
endpoints. Não altere issues nem código.
```

**Resultado esperado:** uma visão de produto verificável, sem hipóteses
disfarçadas de decisão.

## 1. Adaptar a arquitetura ao projeto

Use a arquitetura de referência como organização das responsabilidades, não
como definição automática do domínio. Registre a arquitetura específica do
projeto em [`ARQUITETURA.md`](./ARQUITETURA.md), respeitando as regras
confirmadas no Jira e
[`spec/constitution.md`](./spec/constitution.md).

| Responsabilidade | Local |
|---|---|
| Entidades e regras puras | `server/core/entities/` |
| Casos de uso | `server/core/usecases/` |
| Contratos do core | `server/core/interfaces/` |
| Persistência e integrações | `server/infra/` |
| Controllers HTTP | `server/api/controllers/` |
| Presenters e schemas de saída | `server/api/presenters/` |
| Composição e injeção de dependências | `server/app.py` |

As dependências de negócio apontam para dentro. O core não importa Flask,
SQLAlchemy ou modelos de persistência. A composição concreta das dependências
acontece em `server/app.py`.

**Prompt**

```text
Leia a arquitetura de referência fornecida, as regras de domínio confirmadas
no Jira e spec/constitution.md. Adapte a arquitetura ao projeto de
classificados PUC e documente responsabilidades, dependências e estrutura de
pastas em ARQUITETURA.md.

Diferencie claramente a estrutura existente da estrutura-alvo. Não copie
entidades ou endpoints do exemplo de produtos. Não marque decisões pendentes
como resolvidas e não altere código.
```

**Resultado esperado:** uma arquitetura coerente com o domínio e com o código
que será construído, sem descrever funcionalidades futuras como existentes.

## 2. Especificar cada feature com SDD

Cada feature deve passar pelo fluxo definido em
[`spec/README.md`](./spec/README.md). Use a skill `criar-feature-sdd` quando
for necessário produzir os artefatos SDD.

Para cada história:

1. Crie `spec/features/NNN-nome/` usando o próximo identificador disponível.
2. Escreva `spec.md` em linguagem de produto, com história, critérios de
   aceitação, regras, exclusões e perguntas em aberto.
3. Mantenha a spec como `Rascunho` até a aprovação explícita.
4. Escreva `plan.md` com entidades, casos de uso, interfaces, persistência,
   API e testes.
5. Escreva `tasks.md` em passos pequenos, ordenados e verificáveis; planeje
   testes antes da implementação.
6. Confira que os critérios de aceitação estão mapeados a testes e tarefas.

O projeto acadêmico tem metas de pelo menos quatro histórias de usuário e
duas entidades. Planeje essas metas a partir das necessidades reais; não crie
funcionalidades artificiais apenas para atingir a contagem.

**Prompt**

```text
Crie os artefatos SDD para esta história usando spec/README.md,
spec/constitution.md e os templates existentes.

Separe requisitos confirmados de dúvidas. Não inclua decisões técnicas nos
critérios de aceitação. Gere spec.md, plan.md e tasks.md consistentes entre
si, com testes planejados antes da implementação. Deixe a spec como
"Rascunho" até eu aprová-la explicitamente.

História e contexto:
[cole a história aprovada e as informações confirmadas do Jira]
```

**Resultado esperado:** três artefatos consistentes; nenhuma implementação de
código nesta etapa.

## 3. Criar a estrutura inicial e o ambiente

Antes de criar pastas, confira o repositório e preserve os arquivos existentes.
Para um repositório vazio, a estrutura segue a arquitetura aprovada, incluindo
pacotes Python, testes e especificações.

**Prompt**

```text
Inspecione o repositório e ARQUITETURA.md. Se a estrutura ainda não existir,
crie somente os diretórios e arquivos vazios necessários para:

- server/core/entities/, interfaces/ e usecases/
- server/infra/db/ e gateways/
- server/api/controllers/ e presenters/
- tests/core/entities/, tests/core/usecases/, tests/infra/db/,
  tests/infra/gateways/ e tests/api/
- spec/features/ e os templates previstos no fluxo SDD

Inclua __init__.py onde necessário para os pacotes Python, sem sobrescrever
arquivos existentes. Não crie funcionalidades nem estruturas de front-end
que não estejam no escopo confirmado. Informe o que já existia e o que foi
criado.
```

Prepare Python 3.11 ou superior, o ambiente virtual, Git e GNU Make. Use
`server/requirements.txt` para dependências da aplicação e ferramentas do
projeto. Os comandos `make install`, `make lint`, `make test` e `make check`
devem continuar coerentes com a estrutura.

**Prompt**

```text
Confira README.md, Makefile, server/requirements.txt e setup.cfg. Configure
apenas o necessário para criar o ambiente virtual, instalar dependências,
executar Flake8 e pytest e rodar make check. Preserve as versões e os padrões
já adotados, a menos que haja uma incompatibilidade comprovada. Não adicione
dependências sem necessidade.
```

**Resultado esperado:** ambiente reproduzível e comandos de validação
funcionais.

## 4. Implementar entidades no core

Entidades representam conceitos de negócio e não devem depender de Flask,
SQLAlchemy, Pydantic ou da API.

A entidade `Usuario` existente tem `nome`, `email`, `matricula`, `vinculo` e
`id` opcional. Esses campos descrevem a base atual de persistência; não
presuma que sejam suficientes para autenticação ou para o perfil de
anunciante. Novas entidades e campos devem vir de uma spec aprovada.

**Prompt**

```text
Leia a spec aprovada e os arquivos atuais de server/core/entities/.
Implemente somente as entidades e regras puras exigidas pela spec, mantendo
compatibilidade com os usos existentes.

Não importe Flask, SQLAlchemy, Pydantic ou módulos de infra/api. Não acrescente
campos ou validações não especificados. Escreva ou atualize testes unitários
para os critérios de aceitação relevantes.
```

**Resultado esperado:** entidades puras e testáveis sem banco ou aplicação
web.

## 5. Definir interfaces do core

Uma interface de repositório descreve as operações que os casos de uso
necessitam; ela não revela como os dados são armazenados. A
[`UsuarioRepositoryInterface`](./server/core/interfaces/usuario_repository_interface.py)
é o contrato atual: `buscar_por_id` e `salvar`.

Adicione métodos somente quando um caso de uso aprovado realmente precisar
deles. Por exemplo, não adicione busca por e-mail, autenticação ou listagem
somente por parecerem úteis.

**Prompt**

```text
Leia a spec aprovada, as entidades e
server/core/interfaces/usuario_repository_interface.py.
Defina ou altere o contrato mínimo necessário para os casos de uso descritos.

A interface deve importar entidades do core e não deve importar SQLAlchemy,
Flask, modelos ORM ou gateways. Preserve os métodos existentes quando forem
compatíveis. Explique qualquer método novo pela necessidade do caso de uso.
```

**Resultado esperado:** contratos internos pequenos, sem dependência da
infraestrutura.

## 6. Implementar casos de uso e seus testes

Crie um caso de uso por ação de negócio da spec. Cada um recebe as interfaces
necessárias por injeção de dependência. Os testes unitários usam repositórios
falsos em memória, não SQLite.

Erros de negócio não devem conhecer status HTTP. O controller ou presenter
traduz esses erros na fronteira da API.

**Prompt**

```text
Implemente o caso de uso [nome] conforme a spec aprovada e o plano técnico.
Antes do código de produção, escreva testes unitários para sucesso, erros de
negócio e limites relevantes, usando um repositório falso em memória.

O caso de uso só pode depender de entidades e interfaces do core. Não importe
Flask, SQLAlchemy, controllers ou gateways. Não escolha comportamento para
decisões que a spec deixou em aberto.
```

**Resultado esperado:** regra de negócio testada isoladamente da API e do
banco.

## 7. Modelar o banco e documentar os dados

O modelo SQLAlchemy, `server/infra/db/schema.sql`, a inicialização do banco, a
documentação e os testes devem descrever o mesmo modelo. Use a skill
`manter-modelagem-dados` sempre que dados persistidos forem adicionados,
alterados ou removidos.

O schema atual persiste `Usuario` com `id`, `nome`, `email`, `matricula` e
`vinculo`, incluindo constraints de obrigatoriedade, conteúdo não vazio e
unicidade para e-mail e matrícula. Não altere esse contrato sem requisito
aprovado e plano para bancos já existentes.

**Prompt**

```text
Implemente a alteração de persistência descrita na spec aprovada. Antes,
leia server/infra/db/README.md, schema.sql, models.py, database.py e os testes.

Mantenha SQLAlchemy, schema SQL, constraints, documentação e testes
sincronizados. Verifique se a alteração afeta bancos existentes. Preserve os
dados e proponha/implemente uma migração explícita quando necessária; não
remova nem transforme dados sem regra aprovada. Não misture modelos ORM às
entidades do core.
```

**Resultado esperado:** evolução persistente explícita, documentada e coberta
por testes.

## 8. Implementar gateways

O gateway implementa o contrato do core e converte entre entidades e modelos
SQLAlchemy. O código de domínio recebe e devolve entidades, nunca modelos ORM.

O gateway atual, `UsuarioRepositorySQLAlchemy`, recebe uma fábrica de sessões
e implementa as operações da interface atual.

**Prompt**

```text
Implemente ou altere o gateway necessário para cumprir a interface aprovada.
Leia a interface, as entidades, os modelos SQLAlchemy e os testes existentes.
Injete a fábrica de sessões; não crie uma conexão global dentro do caso de uso.

Converta entre entidades do core e modelos ORM dentro do gateway. Adicione
testes de persistência e consulta para os métodos afetados, incluindo ausência
do registro e constraints pertinentes. Não implemente regras de negócio no
gateway.
```

**Resultado esperado:** persistência substituível atrás do contrato e testes
executados com SQLite de teste.

## 9. Criar presenters e schemas HTTP

Presenters transformam entidades e resultados em respostas públicas. Schemas
Pydantic de entrada e saída pertencem à API, não ao core. Não exponha campos
pessoais sem regra de visibilidade aprovada.

**Prompt**

```text
Leia a spec e o contrato da API. Crie ou altere os presenters e schemas
necessários em server/api/presenters/.

Os presenters podem depender das entidades do core e de Pydantic, mas não
podem importar infra/. Exponha somente os campos autorizados pela spec.
Mantenha a forma de sucesso e erro documentada e teste a conversão relevante.
Não invente campos, mensagens ou regras de visibilidade.
```

**Resultado esperado:** representações de resposta previsíveis sem vazamento
de detalhes de persistência.

## 10. Criar controllers e endpoints

O endpoint atual é `GET /health`. Endpoints de autenticação, perfil e
anúncios só devem ser criados quando houver spec aprovada e plano.

Controllers recebem e validam a entrada HTTP, chamam casos de uso e convertem
erros conhecidos em respostas documentadas. Não instanciam repositórios nem
implementam regras de negócio.

**Prompt**

```text
Implemente somente os endpoints da spec aprovada em
server/api/controllers/. Receba os casos de uso por injeção, valide o
contrato de entrada, chame o caso de uso e use os presenters para as respostas.

Mapeie apenas erros conhecidos para os status HTTP definidos no contrato.
Não importe server/infra/, não crie repositórios e não coloque regras de
negócio no controller. Documente os schemas e status de resposta e teste
sucesso, validação e erros previstos.
```

**Resultado esperado:** camada HTTP fina e coberta por testes de controller.

## 11. Montar a aplicação

`server/app.py` é o composition root: cria a aplicação, configura opções de
ambiente, inicializa persistência e conecta gateways, casos de uso e
controllers. O core não cria suas dependências concretas.

**Prompt**

```text
Revise server/app.py e conecte os componentes necessários para a spec
aprovada. Mantenha a criação de dependências concretas concentrada no
composition root e injete abstrações nos casos de uso/controllers.

Preserve GET /health, a configuração documentada de DATABASE_URL e CORS_ORIGINS
e os testes existentes. Não adicione configuração ou serviço externo sem
requisito.
```

**Resultado esperado:** aplicação montada de forma explícita, iniciável e
testável.

## 12. Integrar o front-end, se fizer parte do escopo

O roteiro de referência inclui `client/scripts.js`, mas o front-end do
classificados fica em `front/` (spec 002), fora de `server/`. Não crie
`client/` nem altere arquivos de interface sem pedido e sem confirmar o
contrato e o escopo.

Quando o front-end for incluído:

1. confirme a localização e os arquivos existentes;
2. valide o contrato dos endpoints;
3. defina tratamento de erros e estados da interface;
4. teste integração API/UI sem expor dados não autorizados.

**Prompt condicional**

```text
Inspecione o front-end fornecido e o contrato aprovado da API. Integre somente
os fluxos solicitados, preservando a estrutura e os estilos existentes.
Use o contrato HTTP confirmado, trate erros de forma visível e não use
innerHTML para inserir dados de usuário. Não crie ou altere telas fora do
escopo. Apresente os arquivos que serão alterados antes de implementar caso
o escopo não esteja claro.
```

## 13. Validar o comportamento

- Rode primeiro os testes focados e depois `make check`.
- Relacione cada critério de aceitação a pelo menos um teste.
- Faça testes unitários do core sem banco; teste gateways com SQLite de teste;
  teste controllers pela API.
- Para cada endpoint novo, teste sucesso, validação, erros de negócio,
  persistência e resposta HTTP, conforme o contrato.
- O smoke test atual é `GET /health`; não use fluxos de Produto do exemplo
  como se existissem no classificados.
- Revise documentação e schema quando a alteração afetar arquitetura ou dados.

**Prompt**

```text
Valide a implementação contra cada critério de aceitação da spec. Execute os
testes focados e make check. Informe comandos, resultados, critérios sem teste
e qualquer comportamento divergente. Não declare cobertura de uma regra que
não foi testada e não altere código fora do escopo para corrigir problemas
preexistentes.
```

## 14. Preparar commits

- Revise `git status` e o diff antes de stagear.
- Separe mudanças por entregas coesas; mantenha código, testes e documentação
  diretamente relacionada juntos.
- Não inclua arquivos de referência ou rascunhos só porque estão no
  repositório.
- Explique cada commit, seus arquivos e a ordem proposta antes de criá-los.
- Depois, confira o histórico e o working tree.

**Prompt**

```text
Revise apenas os arquivos que estão staged. Proponha commits pequenos e
coerentes, listando para cada um os arquivos, o objetivo e os passos na ordem.
Explique a proposta antes de criar qualquer commit. Não stageie arquivos
adicionais sem autorização.
```

## Faz sentido criar uma skill para manter o padrão?

Sim. A skill
[`implementar-feature-classificados`](./.github/skills/implementar-feature-classificados/SKILL.md)
foi criada para implementar features aprovadas seguindo este roteiro. Ela lê
spec/plan/tasks, conduz uma tarefa por vez e valida cada entrega. O roteiro
continua como fonte de verdade; a skill não copia todo o conteúdo:

- `criar-feature-sdd` continua responsável por `spec.md`, `plan.md` e
  `tasks.md`;
- `manter-modelagem-dados` continua responsável por alterações persistentes;
- skills Jira continuam responsáveis pelas operações Jira;
- a skill delega a criação de specs e alterações de dados às skills
  existentes, em vez de duplicar seus procedimentos.

**Manutenção:** atualize este roteiro quando o fluxo estável mudar. Mantenha a
skill curta e alinhada a ele; não duplique aqui ou nela os procedimentos das
skills especializadas.

## Prompts que orientaram a adaptação

As conversas anteriores estabeleceram estes pedidos como base:

1. “Vamos ajustar para o nosso domínio. Utilize como base o `ARQUITETURA.md`
   para ajustar o `ESTRUTURA.md` conforme nossas regras de domínio do Jira.”
2. “Agora o MCP do Jira está conectado. Revise novamente.”
3. “Siga a arquitetura de `ARQUITETURA.md` para adaptar a arquitetura de
   `ESTRUTURA.md`. Vá perguntando passo a passo caso tenha dúvida.”
4. “Reestruture a partir da estrutura de pastas um Markdown. Use como base o
   `ARQUITETURA.md`.”
5. “Siga à risca o `ARQUITETURA.md`.”

O exemplo de 440 linhas acrescenta o formato operacional adotado aqui:
**um prompt por camada, limites explícitos, arquivos esperados, testes e
validação**, adaptado ao nosso domínio e ao estado real do repositório.

Os nomes `ESTRUTURA.md` citados nos prompts históricos são mantidos como
registro do que foi pedido na época; o documento de arquitetura atual se chama
`ARQUITETURA.md`.

## Como manter este roteiro estável

- Mude o roteiro quando o fluxo do projeto ou as fontes de verdade mudarem;
  não o use para registrar cada detalhe de uma feature.
- Mantenha regras de negócio nas specs aprovadas e detalhes técnicos nos
  planos e documentos de arquitetura.
- Em cada prompt, deixe claros o contexto a consultar, o escopo, as proibições,
  os arquivos esperados e a validação.
- Antes de reutilizar um prompt, confira os caminhos e os contratos atuais no
  repositório; os exemplos deste roteiro são guias, não instruções para
  sobrescrever código existente.
- Após alterar o roteiro, verifique links, paths, sequência das etapas e
  consistência com as skills disponíveis.

### Contrato recomendado para a futura skill

Se o fluxo for reutilizado, a skill `implementar-feature-classificados`
deverá:

1. ser acionada somente para implementar uma feature aprovada, não para criar
   requisitos ou decidir questões pendentes;
2. consultar a spec, o plano, as tarefas, a arquitetura, a constituição e este
   roteiro antes de editar código;
3. executar tarefas pequenas em ordem, com testes antes da implementação;
4. usar as skills especializadas de SDD, Jira e modelagem de dados em vez de
   duplicar suas instruções;
5. parar e perguntar quando a próxima tarefa depender de regra não aprovada;
6. validar os critérios de aceitação e os testes aplicáveis e reportar
   claramente o que foi concluído e o que ficou pendente;
7. não stagear nem criar commits automaticamente; se commits forem pedidos,
   explicar a divisão antes de criá-los.
