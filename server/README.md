# API (`server/`)

API em Flask-OpenAPI3 com Clean Architecture. A organização das camadas está
em [ARQUITETURA.md](../ARQUITETURA.md); o
banco, em [infra/db/README.md](infra/db/README.md).

## Executar

```bash
flask --app server.app:create_app run --debug
```

Sobe em http://127.0.0.1:5000. `GET /health` deve responder
`{"status": "ok"}` e a documentação das rotas fica em `/openapi`.

| Variável | Padrão | Uso |
|---|---|---|
| `DATABASE_URL` | `server/database/db.sqlite3` | Localização do banco |
| `CORS_ORIGINS` | — | Origens permitidas, separadas por vírgula; vazio desabilita o CORS |

> **Atualizando de uma versão anterior?** A feature de cadastro e login mudou
> a tabela `usuarios` sem script de migração. Apague
> `server/database/db.sqlite3` antes de subir; o banco é recriado sozinho.
> A extensão da tabela `ads` é migrada automaticamente e preserva anúncios
> existentes. Detalhes em [infra/db/README.md](infra/db/README.md).

## Autenticação e e-mail

O cadastro exige e-mail institucional (`@puc-rio.br` ou `@aluno.puc-rio.br`)
e só termina pelo link de confirmação enviado por e-mail. O login devolve um
token, enviado depois em `Authorization: Bearer <token>`. Rotas em `/auth/*`.

| Variável | Padrão | Uso |
|---|---|---|
| `EMAIL_BACKEND` | `log` | `log` (escreve o e-mail no log) ou `smtp` |
| `SMTP_HOST`, `SMTP_PORT`, `SMTP_USUARIO`, `SMTP_SENHA` | — | Obrigatórias com `smtp` (STARTTLS) |
| `EMAIL_REMETENTE` | — | Endereço "De:"; obrigatória com `smtp` |
| `CONFIRMACAO_URL_BASE` | `http://localhost:5173/confirmar-email` | Página do front que recebe `?token=` |
| `SESSAO_DURACAO_HORAS` | `8` | Validade da sessão |

Com `smtp`, a aplicação não sobe se faltar variável obrigatória. Segredos SMTP
entram só por variável de ambiente.

Em desenvolvimento (`log`), o link de confirmação aparece no terminal. Para
confirmar sem front:

```bash
curl -X POST http://127.0.0.1:5000/auth/confirmacao \
  -H "Content-Type: application/json" -d '{"token": "<token>"}'
```

## Perfil de anunciante e fotos

Rotas protegidas: `GET` e `PUT /perfil-anunciante` e
`GET /fotos-perfil/<arquivo>`. As fotos (JPEG, PNG ou WEBP, até 2 MB) ficam
em disco com nome aleatório; requisições acima de 3 MB recebem `413`.

| Variável | Padrão | Uso |
|---|---|---|
| `FOTOS_PERFIL_DIR` | `server/uploads/fotos_perfil` | Pasta das fotos |

`server/uploads/` está no `.gitignore` e é criada na primeira foto. Faça
backup dela junto com o banco.

## Feed, publicação e imagens de anúncios

`GET /api/ads` lista anúncios de produtos, serviços e eventos. A rota exige
uma sessão válida. `POST /api/ads` também exige sessão e perfil de anunciante
persistido; aceita JSON ou `multipart/form-data` com imagem JPEG, PNG ou WEBP.
Imagens são limitadas a 5 MB por padrão. O feed não usa perfil ou autenticação
mockados.

### `POST /api/ads`

Envie `Authorization: Bearer <token>` e um corpo `application/json` ou
`multipart/form-data`. O perfil de anunciante é conferido antes da leitura e
validação do corpo. O anúncio sempre fica vinculado ao usuário do token; o
cliente não pode enviar `id`, `id_anunciante`, `created_at`,
`nome_anunciante` nem campos desconhecidos.

| Campo | Regras |
|---|---|
| `titulo` | Obrigatório; texto aparado de 5 a 80 caracteres |
| `categoria` | Obrigatória: `produto`, `servico` ou `evento` |
| `estado_conservacao` | Obrigatório para `produto` (`novo` ou `usado_regular`); não se aplica a `servico`/`evento` |
| `descricao` | Obrigatória; texto não vazio de até 500 caracteres |
| `preco` | De 0 a 9999999999,99, com até duas casas decimais; obrigatório quando não é “a combinar” |
| `preco_a_combinar` | Booleano JSON opcional, padrão `false`; em multipart, `"true"` ou `"false"` |
| `imagem` | Opcional, uma foto JPG, PNG ou WebP, respeitando o limite do storage |

Quando `preco_a_combinar` for `true`, omita `preco`. Em JSON, campos de texto
devem ser strings e `preco_a_combinar` deve ser booleano. Corpos JSON acima de
64 KiB recebem `413`; multipart mantém o limite maior necessário para suportar
a foto. A API autentica por Bearer token, portanto não depende de CSRF por
cookie.

Exemplo de produto:

```json
{
  "titulo": "Caderno universitário",
  "categoria": "produto",
  "estado_conservacao": "novo",
  "descricao": "Caderno novo, sem uso.",
  "preco": "10.50"
}
```

Exemplo de serviço:

```json
{
  "titulo": "Aulas de inglês",
  "categoria": "servico",
  "descricao": "Aulas particulares para iniciantes.",
  "preco": 50
}
```

Exemplo de evento com preço a combinar:

```json
{
  "titulo": "Feira comunitária",
  "categoria": "evento",
  "descricao": "Encontro aberto à comunidade.",
  "preco_a_combinar": true
}
```

Sucesso retorna `201` com o formato de card usado pelo feed:

```json
{
  "id": 42,
  "title": "Caderno universitário",
  "description": "Caderno novo, sem uso.",
  "type": "product",
  "category": "produto",
  "price": 10.5,
  "image_url": null,
  "created_at": "2026-11-22T01:49:36Z",
  "nome_anunciante": "Ana Vendas",
  "estado_conservacao": "novo",
  "preco_a_combinar": false
}
```

Um serviço retorna o mesmo formato, com `type: "service"` e
`estado_conservacao: null`; um evento a combinar retorna `type: "event"`,
`estado_conservacao: null`, `price: null` e `preco_a_combinar: true`.

A resposta segue o schema do feed existente: usa `title`/`price` e preço JSON
numérico, não inclui `id_anunciante`, e `created_at` é fornecido pelo relógio
UTC da aplicação. O registro é confirmado antes da resposta e aparece na
consulta seguinte do feed. A persistência preserva o schema atual (`ads.price`
como `Float` e a flag `preco_a_combinar`); não é feita migração para armazenar
preços como `Decimal` nem para representar o preço negociável com `NULL`.
Validações retornam `422` com `campos`; perfil incompleto retorna `403` com
`code: "perfil_incompleto"`. Falta de sessão retorna `401`; JSON malformado
retorna `400`; tipo de conteúdo não aceito retorna `415`. Erros inesperados em
`/api/` são JSON genérico e não expõem detalhes internos.

O storage de anúncio é independente do storage das fotos de perfil. Por padrão,
as imagens ficam em `media/` e são servidas em `/media/<chave>`. Para configurar
storage compatível com S3, use `STORAGE_PROVIDER=s3` e `STORAGE_S3_BUCKET`;
região, endpoint, credenciais, URL pública, expiração de URL assinada e prefixo
podem ser configurados por `STORAGE_S3_REGION`,
`STORAGE_S3_ENDPOINT_URL`, `STORAGE_S3_ACCESS_KEY_ID`,
`STORAGE_S3_SECRET_ACCESS_KEY`, `STORAGE_S3_PUBLIC_BASE_URL`,
`STORAGE_S3_PRESIGN_EXPIRES_SECONDS` e `STORAGE_S3_KEY_PREFIX`.
`STORAGE_MAX_IMAGE_BYTES`, `STORAGE_LOCAL_ROOT` e
`STORAGE_LOCAL_URL_BASE` configuram limite, pasta e caminho local.
