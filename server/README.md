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
