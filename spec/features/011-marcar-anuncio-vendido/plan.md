# Plano técnico: Marcar anúncio como vendido (back-end)

Referência: `spec.md` desta pasta.

## Entities

Sem mudanças. `Ad.publication_ends_at()` (spec 010) decide se a reativação
volta como publicado ou expirado.

## Use cases (`server/core/usecases/alterar_status_anuncio.py`)

| Use case | Entrada | Saída | Erros possíveis |
|----------|---------|-------|-----------------|
| `AlterarStatusAnuncio` | `ad_id`, `usuario_id`, `novo_status` (`sold` ou `published`) | `Ad` atualizado | `AnuncioNaoEncontrado`, `AnuncioDeOutroUsuario`, `StatusInvalido`, `MudancaDeStatusInvalida` |

Usa `buscar_anuncio_do_dono` (spec 007) e o relógio injetado.

Interface: `AnuncioEditavelRepositoryInterface` ganha
`alterar_status(ad_id, status) -> Ad`, implementado em
`AdRepositorySQLAlchemy`.

## Interface web (`server/api/controllers/ads_controller.py`)

| Método | Rota | Corpo | Respostas |
|--------|------|-------|-----------|
| PATCH | `/api/ads/<id>/status` | `{"status": "sold"}` ou `{"status": "published"}` | `200` com o anúncio; `400` corpo inválido; `403`; `404`; `415` sem JSON; `422` mudança inválida |
| GET | `/api/ads?owner=me&status=sold` | — | `200`; `400` se `status=sold` vier sem `owner=me` |

`AdViewSchema` passa a devolver `status` e `expires_at`, para a tela saber em
que lista o anúncio ficou.

## Estratégia de testes

- `tests/core/usecases/test_alterar_status_anuncio.py`: CA1–CA5 com
  repositório em memória e relógio falso.
- `tests/infra/gateways/test_ad_repository_gerenciar.py`: `alterar_status`.
- `tests/api/test_status_anuncio_controller.py`: rota, códigos de resposta,
  feed sem o vendido e listagem de vendidos do dono (CA6).
