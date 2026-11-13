# Plano técnico: Visualizar feed de anúncios

Referência: `spec.md` desta pasta.

Dependências:

- A publicação de anúncios deve estar concluída ou ter seu contrato definido
  pela história PROJ-15.
- Anúncios vendidos ou expirados não são retornados pelo feed; anúncios
  excluídos não devem permanecer disponíveis para consulta.
- A PROJ-15 define expiração automática após 30 dias sem renovação; a
  implementação do feed deve considerar o estado resultante dessa regra.
- O feed é acessado por usuário autenticado da comunidade universitária.

## Domain (`domain/`)

| Entidade | Atributos | Regras/validações |
|----------|-----------|-------------------|
| Ad | id, title, description, type, category, price, image_url, created_at, status, expires_at | `title`, `type`, `category`, `price`, `created_at` e `status` são obrigatórios; `description` e `image_url` podem ser opcionais conforme o contrato de publicação; somente anúncios publicados, não vendidos e não expirados podem aparecer no feed |

O domínio deve representar estados de publicação suficientes para distinguir
anúncios disponíveis de anúncios vendidos ou expirados. A exclusão remove o
anúncio da fonte de consulta, conforme o contrato da PROJ-15. A regra de
expiração pertence ao domínio/use case, e não à rota HTTP.

## Use cases (`use_cases/`)

| Use case | Entrada | Saída | Erros possíveis |
|----------|---------|-------|-----------------|
| ListAds | usuário autenticado, `page` opcional e inteiro positivo, `search` opcional e `type` opcional (`all`, `product` ou `service`); tamanho fixo de 20 | itens do feed e metadados `page`, `per_page`, `total_pages` e `total_items` | usuário não autenticado; parâmetros inválidos; falha de busca |

Interfaces de repositório necessárias:

- `AdRepository`: método `list_published(page, per_page, search, ad_type)` que
  filtra anúncios disponíveis, exclui vendidos e expirados, aplica busca em
  título, descrição e categoria, filtra por tipo quando solicitado, ordena por
  `created_at DESC` e retorna os itens da página e o total.
- A interface deve ser definida em `use_cases/` e não pode depender de SQLite,
  Flask ou qualquer detalhe da infraestrutura.

## Infra (`infra/`)

- Tabela SQLite: `ads`
- Colunas: `id`, `title`, `description`, `type`, `category`, `price`, `image_url`,
  `created_at`, `status`, `expires_at`
- Restrições: `title`, `category`, `price`, `created_at` e `status` obrigatórios;
  `image_url` nulo quando não houver foto; `expires_at` obrigatório quando o
  contrato de publicação definir expiração.
- Consulta: selecionar somente anúncios publicados e disponíveis, excluir
  anúncios vendidos e expirados, aplicar busca e filtro de tipo quando
  informados, ordenar por `created_at DESC`, aplicar `LIMIT 20` e
  `OFFSET (page - 1) * 20`.
- Implementação: `infra/repositories/ad_repository_sqlite.py`
- A inicialização deve criar a tabela sem alterar ou remover a tabela
  `usuarios` existente. Uma eventual migração para bancos já inicializados
  deve ser explícita e testável.
- O repositório não deve conhecer HTTP nem autenticação; recebe somente os
  dados necessários para a consulta.

## Interface web (`app/routes/`)

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

- A barra superior contém o botão `Novo anúncio`.
- A barra superior contém um campo de busca por título, descrição ou categoria.
- O feed oferece os filtros `Todos`, `Produtos` e `Serviços`.
- O feed apresenta uma grade responsiva de cards.
- Cada card exibe foto quando houver, título, categoria, preço e data.
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
- A montagem da rota, do caso de uso e do repositório ocorre na inicialização
  da aplicação.
- A regra de filtragem, disponibilidade, busca, ordenação e paginação fica no
  caso de uso e na abstração do repositório, não na camada HTTP.
- O card, o grid e a paginação são componentes separados, cada um com uma
  responsabilidade visual coesa.
- A integração com a página de detalhes ocorre por navegação, sem duplicar
  regras do caso de uso de detalhes.

## Estratégia de testes

- `tests/domain/`: validar campos obrigatórios, foto opcional e estados
  publicável, vendido e expirado da entidade `Ad`.
- `tests/use_cases/`: testar `ListAds` com repositório em memória para
  autenticação, filtragem de disponíveis, exclusão de vendidos/expirados,
  busca, filtros por tipo, combinação de busca e filtro, retorno à primeira
  página, ordenação, limite de 20, páginas seguintes, página padrão e feed vazio.
- `tests/infra/`: testar consulta SQLite, `LIMIT/OFFSET`, ordenação, exclusão
  de   estados indisponíveis, busca, filtro de tipo e preservação da tabela `usuarios`.
- `tests/app/`: testar status HTTP, formato JSON, autenticação, mensagem de
  feed vazio, parâmetros inválidos e falhas do repositório.
- Testes de interface devem verificar card, descrição resumida de serviço,
  grid responsivo, paginação numerada, busca, filtros, botão `Novo anúncio` e
  navegação para detalhes.
- Cada critério de aceitação deve ter pelo menos um teste correspondente.
