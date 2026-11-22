# Plano técnico: Apagar anúncios expirados há mais de 30 dias

Referência: `spec.md` desta pasta.

## Entities (`server/core/entities/ad.py`)

- `Ad.RETENTION_AFTER_EXPIRY = timedelta(days=30)`.
- `Ad.can_be_deleted(now)`: verdadeiro só para anúncio `expired` com
  `now >= publication_ends_at() + RETENTION_AFTER_EXPIRY` (RN1, RN2).

## Use cases (`server/core/usecases/delete_expired_ads.py`)

| Use case | Entrada | Saída | Erros possíveis |
|----------|---------|-------|-----------------|
| `DeleteExpiredAds` | nenhuma (usa o relógio) | chaves das fotos dos anúncios apagados e quantidade | nenhum de negócio |

Interface (`server/core/interfaces/deletable_ad_repository_interface.py`):

- `list_expired_ads() -> list[Ad]`
- `delete_expired(ad_ids) -> list[str | None]`: apaga os que ainda estão
  expirados e devolve a chave da foto de cada um (ou `None`).

Interface separada (ISP), como a `ExpirableAdRepository` da spec 004.

## Infra

- `DeletableAdRepositorySQLAlchemy`
  (`server/infra/gateways/deletable_ad_repository_sqlalchemy.py`) estende
  `AdRepositorySQLAlchemy` e cumpre a interface nova. Fica em arquivo próprio
  para não mexer no repositório compartilhado. A chave da foto sai direto da
  linha apagada, sem mudar a entidade `Ad`.
- Sem mudança de tabela.

## Entrada (`server/api/comandos.py`)

```
flask --app server.app:create_app apagar-anuncios-expirados
```

O comando chama `DeleteExpiredAds`, apaga as fotos pelo armazenamento de
imagens (falhas só vão para o log, RN4) e imprime
`N anúncio(s) apagado(s).`

## Estratégia de testes

- `tests/core/entities/test_ad.py`: limite exato, expirado recente, publicado
  e vendido antigos.
- `tests/core/usecases/test_delete_expired_ads.py`: CA1–CA5 com repositório
  em memória.
- `tests/infra/gateways/test_ad_repository_delete_expired.py`: listar
  expirados, apagar só os que seguem expirados e devolver as chaves das fotos.
- `tests/api/test_comando_apagar_expirados.py`: comando com foto real no
  armazenamento local.
