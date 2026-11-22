# Plano técnico: Detalhar anúncio

Referência: `spec.md` desta pasta. Decisões gerais:
[`spec/decisoes.md`](../../decisoes.md).

## Dependências e contrato

- A publicação/anúncio deve fornecer, no mínimo, `id`, título, categoria,
  estado de conservação, preço, descrição completa, estado de publicação e
  uma foto opcional. Localização no campus fica fora desta feature.
- A feature depende do contrato da publicação e do perfil de anunciante já
  aprovado.
- O perfil divulgado usa `Anunciante` e `ContatoAnunciante` já existentes.
- A API reutiliza o repositório de anúncios e amplia o dado consultado por id;
  não expõe dados privados do usuário.
- `D-004` exige sessão confirmada em todas as rotas de conteúdo.

## Entities (`server/core/entities/`)

| Entidade | Atributos | Regras/validações |
|---|---|---|
| `AdDetails` (nova, representação do domínio) | dados públicos do anúncio e dados resumidos do anunciante | anúncio publicado e disponível; descrição completa; zero ou uma foto; vínculo e contatos válidos |
| `AdvertiserSummary` (nova, objeto de valor) | `nome_exibicao`, `vinculo`, `foto_url`, contatos públicos | nome obrigatório; vínculo vem da conta; contatos seguem D-013 |

O contrato reutiliza os campos existentes da entidade `Ad`, incluindo a foto
opcional por anúncio. Não criar campos de localização ou constantes soltas no
controller.

## Use cases (`server/core/usecases/`)

| Use case | Entrada | Saída | Erros possíveis |
|---|---|---|---|
| `ObterDetalhesAnuncio` | usuário da sessão, `anuncio_id` inteiro positivo | dados completos do anúncio e resumo público do anunciante | `AnuncioNaoEncontrado`, `AnuncioIndisponivel`, `UsuarioNaoAutenticado` |

### Interfaces (`server/core/interfaces/`)

- `AdRepository`: além da consulta do feed, obter anúncio por id e seus dados
  associados. A interface continua sem conhecer Flask ou SQLAlchemy.
- `AnuncianteRepositoryInterface`: buscar perfil e contatos pelo usuário dono
  do anúncio, reutilizando o contrato existente.
- Interface opcional para fotos do anúncio, caso a modelagem use armazenamento
  separado em vez de URLs persistidas.

## Infra (`server/infra/`)

- Reutilizar o modelo `AdModel` e a entidade `Ad` existentes. Não ampliar o
  contrato com localização ou múltiplas fotos nesta feature.
- Repositório SQLAlchemy usa o `id` técnico, busca o anúncio, verifica estado
  publicado/disponível e carrega o anunciante e contatos.
- Fotos e fotos de perfil são conteúdo protegido por sessão (D-004/D-025). O
  front baixa arquivos autenticados e cria `blob:`; não monta URLs públicas com
  token na query.
- Atualizar `schema.sql`, `server/infra/db/README.md`, modelos e testes juntos
  antes de persistir novos campos.

## Interface web (`server/api/controllers/`)

| Método | Rota | Use case chamado | Resposta |
|---|---|---|---|
| GET | `/api/ads/<anuncio_id>` | `ObterDetalhesAnuncio` | `200` com anúncio completo e perfil resumido; `401` sem sessão; `404` inexistente ou indisponível; `400` id inválido |

Contrato de sucesso esperado:

```json
{
  "ad": {
    "id": 1,
    "title": "Título",
    "category": "Categoria",
    "conservation": null,
    "price": 100.0,
    "description": "Descrição completa",
    "photo_url": null,
    "status": "published",
    "created_at": "2026-11-21T12:00:00Z"
  },
  "advertiser": {
    "display_name": "Nome",
    "affiliation": "aluno",
    "photo_url": null,
    "contacts": []
  }
}
```

Os nomes JSON acima são provisórios e devem seguir o idioma e o contrato da
implementação do feed; campos pendentes ficam em aberto até a aprovação da
spec.

Erros HTTP são apresentados por `server/api/erros_http.py`. Detalhes internos
do banco e SQL não aparecem nas respostas.

## Front-end (`front/anuncios/<id>/`)

- Criar uma página dedicada chamada pelo clique no card do feed.
- Cabeçalho comum e layout responsivo conforme `wireframe.md`: foto à esquerda,
  informações do item à direita.
- Bloco do anunciante abaixo das informações, com nome, vínculo, foto e
  contatos.
- Usar componentes existentes (`painel`, `botao`, `alerta`, `etiqueta`,
  `galeria`/classes novas só em CSS próprio se não houver componente).
- Nenhum dado da API é exibido com `innerHTML`.
- Estados: carregando, sucesso, inexistente/indisponível, falha de conexão,
  sem fotos e sem sessão.
- A foto usa texto alternativo ou rótulo acessível adequado ao layout.
- Links de WhatsApp e demais contatos usam os valores validados do perfil.
- Seguir D-030 a D-034 e `front/css/tema.css`.

## Princípios SOLID

- `ObterDetalhesAnuncio` coordena um único caso de uso e recebe repositórios
  por parâmetro.
- Entidade e use case não conhecem Flask, SQLAlchemy ou URLs de HTTP.
- Repositórios continuam substituíveis por implementações em memória nos testes.
- O presenter traduz entidades em JSON; o controller só traduz entrada, sessão
  e erros HTTP.
- Galeria, informações do item e bloco do anunciante são componentes visuais
  separados.

## Estratégia de testes

- `tests/core/entities/`: anúncio disponível/indisponível, fotos ordenadas,
  resumo do anunciante e ausência de foto.
- `tests/core/usecases/`: sucesso autenticado, id inválido/inexistente,
  excluído, vendido, expirado e não publicado.
- `tests/infra/`: consulta por id, estado disponível, anunciante associado,
  contatos na ordem e ausência de dados privados.
- `tests/api/`: `200`, `400`, `401`, `404`, falha do repositório e contrato
  JSON sem campos internos.
- `front/tests/`: renderização das informações, foto única,
  fallback sem fotos, navegação acessível, contatos, estados de erro e
  responsabilidade visual móvel.
- Cada critério de aceitação da spec deve ter pelo menos um teste.

