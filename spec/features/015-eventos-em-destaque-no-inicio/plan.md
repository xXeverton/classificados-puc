# Plano técnico: Eventos da PUC em destaque na tela inicial

Referência: `spec.md` desta pasta. Só implementar com a spec **Aprovada**
(D-051).

## Entities (`server/core/entities/`)

| Entidade | Atributos | Regras/validações |
|----------|-----------|-------------------|
| `Anuncio` (alterada) | + `data_evento: date \| None`, + `horario_evento: time \| None`, + `local_evento: str \| None` | Categoria `evento` exige `data_evento` (RN2); horário e local opcionais; outras categorias exigem os três vazios (RN3); `local_evento` até `LOCAL_EVENTO_MAX_CARACTERES = 80`. Estado de conservação continua proibido em evento. |
| `Ad` (alterada) | + `data_evento`, `horario_evento`, `local_evento` | Dado de leitura para feed, detalhes e destaques. |

Função pura nova no core: `fim_do_prazo_do_evento(data_evento) -> datetime`
(UTC), que devolve o início do dia seguinte em Brasília (RN4, RN8). O fuso
fica numa constante (`FUSO_DA_PUC = ZoneInfo("America/Sao_Paulo")`).

A regra "a data não pode ter passado" depende do dia atual, por isso fica nos
use cases de publicar e editar (que recebem o relógio), não na entidade.

## Use cases (`server/core/usecases/`)

| Use case | Entrada | Saída | Erros possíveis |
|----------|---------|-------|-----------------|
| `ListarEventosEmDestaque` (novo) | usuário da sessão | até `LIMITE_EVENTOS_EM_DESTAQUE = 5` `Ad` de evento publicados com `data_evento >= hoje`, por data e depois por criação | usuário ausente |
| `PublicarAnuncio` (alterado) | + data, horário e local | como hoje; para evento, `expira_em = fim_do_prazo_do_evento(data)` | data ausente, inválida ou passada; campos de evento fora de evento |
| `EditarAnuncio` (alterado) | + data, horário e local | como hoje; nova data recalcula `expires_at` (CA8) | idem |
| `RenovarAnuncio` (alterado) | — | — | novo erro: evento não é renovado (CA9) |
| `ListAds` (alterado) | + `excluir_eventos: bool = False` | como hoje | — |
| `ObterDetalhesAnuncio` (alterado) | — | inclui data, horário e local | — |

A rotina de expiração (`ExpireAds`, spec 010) não muda: ela já usa
`expires_at`, que agora termina no dia seguinte ao evento. O filtro por
`data_evento >= hoje` no painel cobre o intervalo até a rotina rodar.

Interfaces (`server/core/interfaces/`):

- `EventosEmDestaqueRepository` (nova, ISP): `listar_eventos_futuros(
  a_partir_de: date, limite: int) -> list[Ad]`.
- `AdRepository.list_published` e `publish`: parâmetro opcional
  `excluir_eventos` (padrão `False`) e campos de evento, sem quebrar quem já
  chama.

## Infra (`server/infra/`)

- Tabela `ads`: colunas anuláveis `data_evento` (DATE), `horario_evento`
  (TIME) e `local_evento` (TEXT).
- As colunas são anuláveis e entram em bancos existentes pela rotina de
  inicialização (`user_version = 4`), sem apagar dados; não é preciso recriar
  o banco (mais simples que o previsto em D-043). Atualizar juntos
  `server/infra/db/models.py`, `schema.sql`, `server/infra/db/README.md` e os
  testes do banco (skill `manter-modelagem-dados`).
- `server/infra/gateways/ad_repository_sqlalchemy.py`: implementar
  `listar_eventos_futuros` (status publicado, tipo evento,
  `data_evento >= a_partir_de`, ordem `data_evento, created_at, id`, `LIMIT`),
  gravar/ler os campos novos e aplicar `excluir_eventos`.

## Interface web (`server/api/controllers/`)

| Método | Rota | Use case chamado | Resposta |
|--------|------|------------------|----------|
| GET | `/eventos-destaque` (nova, D-020) | `ListarEventosEmDestaque` | `{"items": [...]}` com 0 a 5 itens (`id`, `title`, `image_url`, `data_evento`); exige sessão (D-004, D-021) |
| POST | publicação existente | `PublicarAnuncio` | aceita `data_evento` (`AAAA-MM-DD`), `horario_evento` (`HH:MM`) e `local_evento`; erros por campo (D-022) |
| edição existente | edição existente | `EditarAnuncio` | idem |
| renovação existente | renovação existente | `RenovarAnuncio` | erro com `codigo` para evento |
| GET | feed existente | `ListAds` | sem filtro de tipo, não traz eventos (CA21); o filtro "Eventos" traz os publicados |
| GET | detalhes existente | `ObterDetalhesAnuncio` | + `data_evento`, `horario_evento`, `local_evento` |

Presenter converte `date` para `AAAA-MM-DD` e `time` para `HH:MM`. Controller
só traduz HTTP.

## Front-end (`front/`, D-030 a D-036)

- `front/inicio/index.html`: seção "Eventos em destaque" acima da busca e do
  feed, oculta por padrão (`hidden`).
- `front/js/dominio/destaques.js` (novo, sem DOM): índice circular
  (próximo/anterior), decidir se há carrossel (mais de 1 item), formatar data,
  constante `INTERVALO_CARROSSEL_MS = 6000`.
- `front/js/paginas/destaques.js` (novo): busca `/eventos-destaque`, monta os
  slides só com DOM e `textContent` (D-031), imagens por `resolverUrlRecurso`
  e links por `ROTAS` (D-036). Slide com imagem, título e data apenas. Troca
  automática com timer limpo em hover/foco e desligado com
  `prefers-reduced-motion`. Setas, pontos e região `aria-live` para o slide
  atual.
- `front/js/paginas/inicio.js`: oculta o painel com busca/filtro (CA20) e
  pede o feed com `excluir_eventos` quando não há filtro (CA21).
- `front/css/destaques.css` (novo), só com variáveis de `:root` (D-034). O
  carrossel serve só ao início, então não entra no `tema.css`.
- `front/anuncios/novo/index.html` e `front/js/paginas/anuncios_novo.js`:
  campos "Data do evento", "Horário" e "Local" só na categoria evento,
  escondendo "Estado de conservação"; validação local só do que não depende
  do servidor (D-033). Textos em `front/js/dominio/mensagens.js`.
- `front/js/paginas/detalhes_anuncio.js`: mostra data, horário e local.
- `front/js/paginas/meus_anuncios.js`: não mostra "Renovar" para eventos.

## Princípios SOLID aplicados

- S: um use case novo só para os destaques; a regra de prazo numa função pura;
  formato HTTP no presenter.
- O: limite, intervalo e fuso em constantes; `ListAds` ganha opção sem mudar
  quem o usa.
- I: `EventosEmDestaqueRepository` com um método, sem inchar `AdRepository`.
- D: relógio e repositório entram por injeção, montados em `server/app.py`.

## Estratégia de testes

- `tests/core/entities/`: `Anuncio` com evento (data obrigatória, horário e
  local opcionais, proibidos em outras categorias, limite do local);
  `fim_do_prazo_do_evento` (virada do dia em Brasília).
- `tests/core/usecases/` (repositório e relógio falsos): destaques (máx. 5,
  ordem, empate, evento de hoje, passado fora, expirado/excluído/sem data
  fora, vazio); publicar evento (sem data, passada, hoje, prazo no dia
  seguinte, mesmo a mais de 30 dias); editar data recalcula o prazo; renovar
  evento falha; `ListAds` com `excluir_eventos`; expiração no dia seguinte.
- `tests/infra/`: gateway dos destaques e colunas novas no schema.
- `tests/api/`: `/eventos-destaque` (sem sessão, com sessão, vazio);
  publicação/edição com data, horário e local; renovação de evento; detalhes.
- Front: `node --test` em `front/js/dominio/destaques.js`; telas por roteiro
  manual (CA1 a CA24).
