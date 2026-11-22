# Plano técnico: Editar e excluir anúncio

Referência: `spec.md` desta pasta.

## Entities (`server/core/entities/`)

- `Ad` ganha `usuario_id: int | None` (dono) e `image_key: str | None`, lidos
  do banco. O presenter não expõe esses campos.
- `Anuncio` (publicação) continua validando os campos editáveis (RN2).

## Use cases (`server/core/usecases/`)

| Use case | Entrada | Saída | Erros possíveis |
|----------|---------|-------|-----------------|
| `EditarAnuncio` | `ad_id`, `Anuncio` com o usuário logado | `Ad` atualizado | `AnuncioNaoEncontrado`, `AnuncioDeOutroUsuario`, `CategoriaNaoEditavel` |
| `ExcluirAnuncio` | `ad_id`, `usuario_id` | `image_key` do anúncio apagado (ou `None`) | `AnuncioNaoEncontrado`, `AnuncioDeOutroUsuario` |

Interface (`server/core/interfaces/anuncio_editavel_repository_interface.py`):

- `buscar_por_id(ad_id) -> Ad | None`
- `atualizar(ad_id, anuncio) -> Ad`: troca título, descrição, preço,
  "a combinar" e estado de conservação; mantém datas, situação e foto.
- `excluir(ad_id) -> None`

Interface separada da `AdRepository` do feed (ISP), para não obrigar os
repositórios falsos do feed a implementar edição.

## Infra (`server/infra/gateways/ad_repository_sqlalchemy.py`)

- `AdRepositorySQLAlchemy` passa a cumprir também a interface nova.
- Sem mudança de tabela: `ads.usuario_id` já existe.

## Interface web (`server/api/controllers/ads_controller.py`)

| Método | Rota | Use case | Resposta |
|--------|------|----------|----------|
| PUT | `/api/ads/<id>` | `EditarAnuncio` | `200` com o anúncio; `404`; `403`; `415` sem JSON; `422` com `campos` |
| DELETE | `/api/ads/<id>` | `ExcluirAnuncio` | `204`; `404`; `403` |

- O `PUT` aceita só JSON e reaproveita a validação do `POST`.
- Depois do `DELETE`, o controller apaga a foto do armazenamento; se isso
  falhar, registra no log, mas a exclusão já valeu.

## Estratégia de testes

- `tests/core/usecases/test_gerenciar_anuncio.py`: CA2, CA5, CA6, RN3 e RN4
  com repositório em memória.
- `tests/infra/gateways/test_ad_repository_gerenciar.py`: buscar, atualizar
  sem mexer em datas e foto, excluir.
- `tests/api/test_gerenciar_anuncio_controller.py`: rotas, códigos de
  resposta, feed mostrando o preço novo (CA1) e sem o anúncio excluído (CA4).
