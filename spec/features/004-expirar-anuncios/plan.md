# Plano técnico: Expirar anúncios não renovados

Referência: `spec.md` desta pasta.

## Entities (`server/core/entities/`)

| Entidade | Atributos | Regras/validações |
|----------|-----------|-------------------|
| `Ad` (existente) | sem atributos novos | `PUBLICATION_PERIOD = timedelta(days=30)` (RN1). `publication_ends_at()` devolve `expires_at` ou, se vazio, `created_at + PUBLICATION_PERIOD` (RN2, RN3). `is_overdue(now)` é verdadeiro só para anúncio `published` com `now >= publication_ends_at()` (RN4, RN5). |

A regra fica na entidade para que a renovação (PROJ-40) e a exclusão
(PROJ-41) usem o mesmo cálculo de prazo.

## Use cases (`server/core/usecases/`)

| Use case | Entrada | Saída | Erros possíveis |
|----------|---------|-------|-----------------|
| `ExpireAds` (`expire_ads.py`) | nenhuma (usa o relógio injetado) | quantidade de anúncios expirados | nenhum de negócio |

Fluxo: lê o instante atual do relógio, busca os anúncios publicados, filtra com
`Ad.is_overdue` e pede ao repositório que marque os vencidos como expirados.

Interfaces necessárias (`server/core/interfaces/`):

- `ExpirableAdRepository` (nova, `expirable_ad_repository_interface.py`):
  `list_published_ads() -> list[Ad]` e
  `mark_as_expired(ad_ids: list[int]) -> int`. Interface separada da
  `AdRepository` do feed (ISP): o feed não precisa dessas operações e o
  repositório falso do feed não muda.
- `RelogioInterface` (existente).

## Infra (`server/infra/`)

- Tabelas/colunas: nenhuma mudança no schema. `ads.status` já aceita
  `expired` e `ads.expires_at` já existe.
- Modelo: `created_at` e `expires_at` de `AdModel` passam a usar o tipo
  `UTCDateTime`, como as outras tabelas. Antes, o SQLite devolvia essas datas
  sem fuso, e comparar com o relógio (UTC com fuso) gerava erro. A coluna
  continua `DATETIME` e os dados gravados continuam válidos; o feed passa a
  devolver as datas com `+00:00`.
- `AdRepositorySQLAlchemy` passa a cumprir também `ExpirableAdRepository`.
  `mark_as_expired` só altera linhas que ainda estão `published`, para não
  sobrescrever um anúncio vendido entre a leitura e a escrita.

## Interface (entrada)

Não há rota HTTP: a rotina não é uma ação de usuário. Ela entra por um comando
de linha do Flask, registrado em `server/app.py`:

```
flask --app server.app:create_app expirar-anuncios
```

| Comando | Use case chamado | Saída |
|---------|------------------|-------|
| `expirar-anuncios` | `ExpireAds` | `N anúncio(s) expirado(s).` |

O comando fica em `server/api/comandos.py`, ao lado dos controllers, por ser
outro adaptador de entrada. Um agendador externo (cron, Agendador de Tarefas
do Windows) chama o comando, por exemplo uma vez por hora.

## Princípios SOLID aplicados

- **S**: `ExpireAds` só expira anúncios; o comando só traduz o resultado em
  texto.
- **I**: `ExpirableAdRepository` é pequena e separada da interface do feed.
- **D**: `ExpireAds` recebe repositório e relógio por injeção.

## Estratégia de testes

- `tests/core/entities/test_ad.py`: prazo pelo `expires_at`, prazo padrão de
  30 dias, limite exato, situação diferente de publicado.
- `tests/core/usecases/test_expire_ads.py`: CA1 a CA6 com repositório em
  memória e `RelogioFalso`.
- `tests/infra/gateways/test_ad_repository_sqlalchemy.py`: listagem só de
  publicados e `mark_as_expired` sem tocar em vendidos.
- `tests/api/test_comando_expirar_anuncios.py`: o comando expira os vencidos,
  imprime a quantidade e o anúncio some do `GET /api/ads`.
