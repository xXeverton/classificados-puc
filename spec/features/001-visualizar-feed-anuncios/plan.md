# Plano técnico: Visualizar feed de anúncios

Referência: `spec.md` desta pasta.

Dependências:

- A publicação de anúncios deve estar concluída ou ter seu contrato definido
  pela história PROJ-15.
- Anúncios vendidos ou expirados (por status ou `expires_at`) não são
  retornados pelo feed; anúncios excluídos não devem permanecer disponíveis
  para consulta.
- A PROJ-15 define expiração automática após 30 dias sem renovação; a
  implementação do feed deve considerar o estado resultante dessa regra.
- O feed é acessado por usuário autenticado da comunidade universitária.

## Domínio (`server/core/entities/`)

| Entidade | Atributos | Regras/validações |
|----------|-----------|-------------------|
| Ad | id, title, description, type, category, price, image_url, created_at, status, expires_at, usuario_id, nome_anunciante, estado_conservacao, preco_a_combinar | `type` aceita `product`, `service` e `event`; foto, anunciante e conservação podem ser nulos para registros antigos ou categorias sem conservação |

O domínio distingue anúncios publicados, vendidos e expirados. Publicações
novas recebem prazo de 30 dias no caso de uso; o repositório não lista anúncios
cujo `expires_at` já passou. A regra não pertence à rota HTTP.

## Casos de uso (`server/core/usecases/`)

| Use case | Entrada | Saída | Erros possíveis |
|----------|---------|-------|-----------------|
| ListAds | usuário autenticado, `page` opcional e inteiro positivo, `search` opcional e `type` opcional (`all`, `product`, `service` ou `event`); tamanho fixo de 20 | itens do feed e metadados `page`, `per_page`, `total_pages` e `total_items` | usuário não autenticado; parâmetros inválidos; falha de busca |

Interfaces de repositório necessárias:

- `AdRepository`: método `list_published(page, per_page, search, ad_type)` que
  filtra anúncios disponíveis, exclui vendidos e expirados, aplica busca em
  título, descrição e categoria, filtra por tipo quando solicitado, ordena por
  `created_at DESC` e retorna os itens da página e o total.
- A interface `AdRepository` fica em `server/core/interfaces/` e não depende
  de SQLite, Flask ou qualquer detalhe da infraestrutura.

## Infraestrutura (`server/infra/`)

- Tabela SQLite: `ads`
- Colunas: campos principais do anúncio, `usuario_id`,
  `estado_conservacao`, `preco_a_combinar` e `image_key`
- Restrições: `title`, `category`, `price`, `created_at` e `status` obrigatórios;
  `type` aceita `product`, `service` e `event`; campos adicionais preservam
  compatibilidade com anúncios existentes.
- Consulta: selecionar somente anúncios publicados e disponíveis, excluir
  anúncios vendidos e expirados por status ou prazo, aplicar busca e filtro de
  tipo quando informados, ordenar por `created_at DESC`, aplicar `LIMIT 20` e
  `OFFSET (page - 1) * 20`.
- Implementação: `server/infra/gateways/ad_repository_sqlalchemy.py`.
- `server/infra/db/migrations/0002_ads_publication.sql` migra a tabela
  existente preservando os anúncios anteriores.
- O repositório não deve conhecer HTTP nem autenticação; recebe somente os
  dados necessários para a consulta.

## API (`server/api/controllers/`)

| Método | Rota | Use case chamado | Resposta |
|--------|------|------------------|----------|
| GET | `/api/ads?page={page}&search={search}&type={type}` | `ListAds` | HTTP 200 com itens e metadados de paginação |

Contrato de sucesso:

```json
{
  "items": [
    {
      "id": 1,
      "title": "Título do anúncio",
      "description": "Descrição do anúncio",
      "type": "product",
      "category": "Categoria",
      "price": 100.0,
      "image_url": null,
      "nome_anunciante": "Nome de exibição",
      "preco_a_combinar": false,
      "created_at": "2026-11-12T10:00:00Z"
    }
  ],
  "page": 1,
  "per_page": 20,
  "total_pages": 1,
  "total_items": 1
}
```

Quando não houver anúncios publicados, a resposta será HTTP 200 com `items`
vazio, metadados zerados e uma mensagem informativa:

```json
{
  "items": [],
  "page": 1,
  "per_page": 20,
  "total_pages": 0,
  "total_items": 0,
  "message": "Nenhum anúncio publicado encontrado."
}
```

Parâmetros inválidos devem retornar HTTP 400 com mensagem explícita. Usuários
não autenticados devem receber a resposta definida pelo mecanismo de
autenticação da aplicação. Falhas inesperadas de persistência devem retornar
HTTP 500 sem expor detalhes de SQL.

## Interface visual

- Interface estática em `front/`, com módulos de página, fluxo, domínio e
  adaptadores em `front/js/`.
- A barra superior contém o botão `Novo anúncio`.
- A barra superior contém um campo de busca por título, descrição ou categoria.
- O feed oferece os filtros `Todos`, `Produtos`, `Serviços` e `Eventos`.
- O feed apresenta uma grade responsiva de cards.
- Cada card exibe foto quando houver, título, categoria, preço e data; mostra
  o nome do anunciante quando disponível e "A combinar" para preço negociável.
- Cards de serviços podem exibir uma descrição resumida.
- Quando não houver foto, o card deve manter sua estrutura sem quebrar o
  layout; o tratamento visual exato deve seguir o wireframe aprovado.
- A navegação usa paginação numerada, mantendo a página atual na URL e
  solicitando os dados correspondentes aos parâmetros de
  `/api/ads?page={page}&search={search}&type={type}`.
- Aplicar ou alterar busca ou filtro retorna a paginação para a primeira página.
- Clicar em um card direciona o usuário para a página de detalhes do anúncio,
  implementada pela história PROJ-17.

## Princípios SOLID aplicados

- A rota não acessa o banco diretamente.
- O use case depende de uma interface de repositório.
- O repositório SQLite implementa essa interface.
- A montagem do controller, do caso de uso e do repositório ocorre em
  `server/app.py`.
- A regra de filtragem, disponibilidade, busca, ordenação e paginação fica no
  caso de uso e na abstração do repositório, não na camada HTTP.
- O card, o grid e a paginação são componentes separados, cada um com uma
  responsabilidade visual coesa.
- A integração com a página de detalhes ocorre por navegação, sem duplicar
  regras do caso de uso de detalhes.

## Estratégia de testes

- `tests/core/entities/`: validar campos obrigatórios, foto opcional e estados
  publicável, vendido e expirado da entidade `Ad`.
- `tests/core/usecases/`: testar `ListAds` com repositório em memória para
  autenticação, filtragem de disponíveis, exclusão de vendidos/expirados,
  busca, filtros por tipo, combinação de busca e filtro, retorno à primeira
  página, ordenação, limite de 20, páginas seguintes, página padrão e feed vazio.
- `tests/infra/gateways/` e `tests/infra/db/`: testar consulta SQLAlchemy,
  migração, `LIMIT/OFFSET`, ordenação, exclusão de estados indisponíveis,
  busca, filtros e preservação dos dados existentes.
- `tests/api/`: testar status HTTP, formato JSON, autenticação, mensagem de
  feed vazio, parâmetros inválidos e falhas do repositório.
- `front/tests/`: testar card, descrição resumida de serviço,
  grid responsivo, paginação numerada, busca, filtros, botão `Novo anúncio` e
  navegação para detalhes.
- Cada critério de aceitação deve ter pelo menos um teste correspondente.
