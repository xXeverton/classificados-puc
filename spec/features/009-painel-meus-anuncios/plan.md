# Plano técnico: Painel "Meus Anúncios"

Referência: `spec.md` desta pasta.

Dependências:

- Usuário autenticado pela sessão existente.
- Contratos `GET /api/ads?owner=me&status={status}&page={page}` e
  `POST /api/ads/<id>/renovar`.
- Contratos de edição e exclusão definidos pela PROJ-38/spec 007.
- Renovar só aceita anúncios expirados próprios.

## Domínio (`server/core/entities/`)

Nenhuma entidade nova é presumida. A entidade `Ad` já representa os dados
necessários ao card e seu vínculo com `usuario_id`; mudanças só serão feitas
se o contrato aprovado exigir informações ainda não disponíveis.

## Casos de uso (`server/core/usecases/`)

| Use case | Entrada | Saída | Erros possíveis |
|----------|---------|-------|-----------------|
| ListarMeusAnuncios | usuário da sessão e página opcional | anúncios publicados pertencentes ao usuário | usuário não autenticado; página inválida; falha de consulta |

A interface do repositório deve ser ampliada ou criada somente após confirmar
como os anúncios próprios serão consultados. O filtro por dono não pode ser
feito pelo controller; pertence à consulta do caso de uso/repositório.

## Infraestrutura (`server/infra/`)

- Nenhuma mudança persistida é necessária.
- Ampliar `AdRepository` com um filtro de proprietário na consulta publicada.
- A consulta limita os resultados a `status == published`, à disponibilidade
  pelo prazo e ao `usuario_id` da sessão.
- Os resultados são ordenados por `created_at DESC`.
- A listagem usa 20 itens por página.
- Qualquer mudança em SQLite, modelo ou schema seguirá a
  `manter-modelagem-dados`; esta feature não presume migração.

## API (`server/api/controllers/`)

| Método | Rota | Use case chamado | Resposta |
|--------|------|-----------------|----------|
| GET | `/api/ads?owner=me&status=published&page={page}` | `ListAds` | Lista paginada dos anúncios publicados do usuário |
| GET | `/api/ads?owner=me&status=expired&page={page}` | `ListAds` | Lista paginada dos anúncios expirados do usuário |
| POST | `/api/ads/<id>/renovar` | `RenovarAnuncio` | 200 com o anúncio renovado; 403 para outro dono; 404 se inexistente; 422 se não estiver expirado |

- `owner=me` é interpretado pelo controller como o usuário autenticado;
  o valor não é usado como id recebido do cliente.
- O endpoint reaproveita `ListAds` com filtros de proprietário e estado.
- Editar usa `PUT /api/ads/<id>`, excluir usa `DELETE /api/ads/<id>` e renovar
  usa `POST /api/ads/<id>/renovar`.

## Interface visual (`front/`)

- Nova tela em uma pasta própria, seguindo o padrão de rotas já usado em
  `front/`.
- Tela acessada pelo link “Meus anúncios” no perfil.
- Cards mostram anúncio publicado com foto, título, categoria, preço, data e
  estado aplicável.
- Cada card oferece Editar, Excluir e Renovar.
- Paginação numerada segue o padrão já usado pelo feed.
- Módulos separados em `front/js/paginas/`, `front/js/fluxos/`,
  `front/js/dominio/` e `front/js/adaptadores/`, sem `innerHTML`.
- Card sem foto deve manter um estado visual válido.
- O formulário aberto por Editar carrega os valores atuais do anúncio.
- A lista usa uma coluna no painel e adapta o card a telas estreitas sem
  overflow horizontal.
- Estados de carregamento, lista vazia, sessão expirada e erro de API devem ser
  explícitos.
- Visuais e componentes existentes em `front/css/tema.css` e no guia de estilo.
- A navegação para o painel pode ser feita por uma entrada na interface aprovada,
  mas a localização exata precisa ser definida junto com a aprovação da tela.

## Princípios SOLID aplicados

- O controller traduz sessão e HTTP, sem aplicar regras de propriedade.
- O caso de uso consulta a propriedade pela abstração do repositório.
- O adaptador HTTP somente chama o contrato aprovado e entrega dados ao fluxo.
- Os módulos do front separam apresentação, fluxo de dados e adaptação HTTP.

## Estratégia de testes

- `tests/core/usecases/`: lista vazia, dono correto, exclusão de anúncios de
  outros usuários e falha de consulta em repositório em memória.
- `tests/infra/gateways/`: consulta por usuário e estados confirmados pelo PO.
- `tests/api/`: autenticação, resposta vazia, sucesso e falha do contrato.
- `front/tests/`: renderização de cards, estado sem foto, lista vazia,
  sessão expirada, falha de conexão e navegação aprovada.
- Cada critério de aceitação terá pelo menos um teste após a aprovação da spec.
