# Tarefas: Visualizar feed de anúncios

Referências: `spec.md`, `plan.md` e `wireframe.md`.

## Domain

- [ ] T1: Escrever testes da entidade `Ad` para campos obrigatórios, foto opcional e estados publicado, vendido e expirado.
- [ ] T2: Implementar a entidade `Ad` em `domain/`.

## Use cases

- [ ] T3: Definir a interface `AdRepository` com paginação, busca, filtro de tipo e total de itens.
- [ ] T4: Escrever testes de `ListAds` com repositório em memória para autenticação e filtragem de anúncios disponíveis.
- [ ] T5: Escrever testes de `ListAds` para filtrar anúncios vendidos e expirados.
- [ ] T6: Escrever testes de `ListAds` para busca em título, descrição e categoria, sem diferenciar maiúsculas e minúsculas.
- [ ] T7: Escrever testes de `ListAds` para filtros Todos, Produtos e Serviços, inclusive combinados com a busca.
- [ ] T8: Escrever testes de `ListAds` para ordenação por data decrescente, limite fixo de 20, páginas numeradas e retorno à primeira página após filtro.
- [ ] T9: Escrever testes de `ListAds` para página padrão, feed vazio, parâmetros inválidos e usuário não autenticado.
- [ ] T10: Implementar o caso de uso `ListAds` em `use_cases/`.

## Infra

- [ ] T11: Atualizar o schema SQLite com a tabela `ads`, seus campos, estados e restrições, preservando `usuarios`.
- [ ] T12: Atualizar a documentação de modelagem em `infra/db/README.md`.
- [ ] T13: Atualizar ou criar migração explícita para bancos já inicializados, se necessária.
- [ ] T14: Escrever testes do repositório SQLite para filtragem de disponibilidade, busca, filtros por tipo, ordenação, `LIMIT/OFFSET` e total.
- [ ] T15: Implementar `AdRepositorySqlite` em `infra/repositories/`.

## Web

- [ ] T16: Escrever testes da rota `GET /api/ads` para resposta paginada, campos dos cards, busca, filtros e feed vazio.
- [ ] T17: Escrever testes da rota para autenticação, parâmetros ausentes ou inválidos e falha do repositório.
- [ ] T18: Criar a rota `GET /api/ads` em `app/routes/`.
- [ ] T19: Registrar a rota e montar as dependências em `app/main.py`.

## Interface visual

- [ ] T20: Escrever testes do card para campos obrigatórios, foto opcional, tipo, descrição resumida de serviço e clique para detalhes.
- [ ] T21: Implementar o componente de Card de Anúncio com os dados retornados pela API.
- [ ] T22: Escrever testes do grid responsivo, da busca, dos filtros, da paginação numerada e do estado vazio.
- [ ] T23: Implementar o grid responsivo do feed, o campo de busca e os filtros `Todos`, `Produtos` e `Serviços`.
- [ ] T24: Implementar a paginação numerada preservando busca e filtro e retornando à primeira página quando forem alterados.
- [ ] T25: Implementar a barra superior com o botão `Novo anúncio`.
- [ ] T26: Implementar a navegação do card para a página de detalhes da PROJ-17.

## Validação

- [ ] T27: Executar `pytest` e confirmar que cada critério de aceitação possui teste passando.
- [ ] T28: Executar `flake8` sem erros.
- [ ] T29: Conferir o contrato da resposta JSON, a autenticação, a busca, os filtros, a mensagem de feed vazio e o limite fixo de 20 itens.
- [ ] T30: Conferir a conformidade com o [wireframe.md](wireframe.md): barra superior, busca, filtros, grade de cards e paginação.
