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

## Expiração de anúncios

Um anúncio publicado vale por 30 dias, contados da publicação ou da última
renovação (`expires_at`). Anúncios vencidos não saem do feed sozinhos: o
comando abaixo os marca como `expired` e informa quantos expirou. Ele pode
rodar quantas vezes for preciso; vendidos e já expirados não mudam.

```bash
flask --app server.app:create_app expirar-anuncios
```

Agende o comando para rodar periodicamente, por exemplo uma vez por hora:

- Linux/macOS (cron): `0 * * * * cd /caminho/do/projeto && .venv/bin/flask --app server.app:create_app expirar-anuncios`
- Windows: crie uma tarefa no Agendador de Tarefas que rode
  `.venv\Scripts\flask.exe --app server.app:create_app expirar-anuncios`
  com a pasta do projeto como diretório inicial.

Regras e critérios: [spec 004](../spec/features/004-expirar-anuncios/spec.md).

### Apagar anúncios expirados

Um anúncio expirado fica guardado por mais 30 dias depois do fim do prazo,
para ainda poder ser renovado. Depois disso, o comando abaixo o apaga de vez,
junto com a foto, e informa quantos apagou. Anúncios publicados e vendidos
nunca são apagados. Se uma foto não puder ser apagada, o anúncio continua
apagado e a falha vai para o log.

```bash
flask --app server.app:create_app apagar-anuncios-expirados
```

Agende-o como o `expirar-anuncios`, por exemplo uma vez por dia. Regras:
[spec 008](../spec/features/008-apagar-anuncios-expirados/spec.md).

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

## Storage de imagens

O módulo `server/infra/storage/storage.py` oferece uma interface única para
armazenamento local e buckets compatíveis com S3. Não há outro provedor de
hospedagem nem infraestrutura como código configurada neste repositório;
`boto3` já faz parte de `server/requirements.txt`. O endpoint atual de anúncios
já usa essa camada para uma foto opcional; não é necessário criar outro endpoint
para configurar o storage.

As imagens são aceitas somente quando a assinatura do conteúdo corresponde a
JPEG, PNG ou WebP, independentemente do nome ou do `Content-Type` informado.
O limite padrão é 5 MiB. A chave é aleatória e imutável, no formato
`namespace/uuid.ext`; persista `image_key`, nunca a URL, pois ela é gerada
quando o anúncio é lido. As respostas enviam `Cache-Control` imutável.

### Variáveis de ambiente

| Variável | Padrão | Uso |
|---|---|---|
| `STORAGE_PROVIDER` | `local` | `local` para desenvolvimento/testes ou `s3` |
| `STORAGE_MAX_IMAGE_BYTES` | `5242880` | Limite de bytes por imagem |
| `STORAGE_LOCAL_ROOT` | `media` | Diretório raiz do provedor local |
| `STORAGE_LOCAL_URL_BASE` | `/media` | Prefixo da rota local |
| `STORAGE_S3_BUCKET` | — | Obrigatória com `s3` |
| `STORAGE_S3_REGION` | — | Região do bucket, se necessária |
| `STORAGE_S3_ENDPOINT_URL` | — | Endpoint de MinIO, R2 ou serviço compatível |
| `STORAGE_S3_ACCESS_KEY_ID` | — | Credencial explícita opcional |
| `STORAGE_S3_SECRET_ACCESS_KEY` | — | Deve ser definida junto com a access key |
| `STORAGE_S3_PUBLIC_BASE_URL` | — | Base pública/CDN; vazia usa URL pré-assinada |
| `STORAGE_S3_PRESIGN_EXPIRES_SECONDS` | `3600` | Validade da URL pré-assinada |
| `STORAGE_S3_KEY_PREFIX` | — | Prefixo opcional dentro do bucket |

As mesmas variáveis estão listadas em [`.env.example`](../.env.example).
O app lê variáveis do ambiente e `app.config`; o arquivo `.env.example` é um
modelo, não é carregado automaticamente. Não salve credenciais reais no
repositório. Quando as chaves explícitas não forem configuradas, `boto3` usa
sua cadeia padrão de credenciais (por exemplo, uma role da aplicação).

### Desenvolvimento local

Não é necessária nenhuma credencial ou conexão externa:

```bash
export STORAGE_PROVIDER=local
export STORAGE_LOCAL_ROOT=media
export STORAGE_LOCAL_URL_BASE=/media
flask --app server.app:create_app run
```

O diretório é criado quando necessário e está coberto pelo `.gitignore`.
`GET /media/<chave>` só é registrado no provedor local, não lista diretórios,
valida a chave e responde com o tipo detectado, `X-Content-Type-Options:
nosniff` e cache imutável. Disco local não é adequado a deploys com filesystem
efêmero ou contêineres recriados; em produção use S3 compatível ou sirva a
pasta por um servidor web/proxy persistente.

### Configurar um bucket S3 compatível

1. Crie o bucket na região escolhida e mantenha o bloqueio de acesso público
   ativado. Não habilite ACL pública nos objetos.
2. Crie uma role/identidade de serviço para a aplicação com acesso somente aos
   objetos do prefixo que ela usa. Exemplo para `STORAGE_S3_KEY_PREFIX=classificados`
   e o namespace de anúncios `anuncios`:

   ```json
   {
     "Version": "2012-10-17",
     "Statement": [
       {
         "Effect": "Allow",
         "Action": [
           "s3:PutObject",
           "s3:GetObject",
           "s3:DeleteObject"
         ],
         "Resource": "arn:aws:s3:::example-classificados/classificados/anuncios/*"
       }
     ]
   }
   ```

   Troque `example-classificados` pelo nome do bucket. A política não permite
   listar nem administrar o bucket. Para outros namespaces, conceda somente os
   caminhos de objeto necessários.
3. Configure `STORAGE_PROVIDER=s3`, `STORAGE_S3_BUCKET` e, quando aplicável,
   `STORAGE_S3_REGION`, `STORAGE_S3_ENDPOINT_URL` e
   `STORAGE_S3_KEY_PREFIX`. Para credenciais estáticas, defina
   `STORAGE_S3_ACCESS_KEY_ID` e `STORAGE_S3_SECRET_ACCESS_KEY` juntas em um
   gerenciador seguro de segredos; prefira a role/credencial de ambiente.
4. Por padrão, não defina `STORAGE_S3_PUBLIC_BASE_URL`: a API gera URLs
   pré-assinadas de leitura, válidas por `STORAGE_S3_PRESIGN_EXPIRES_SECONDS`
   (3600 segundos por padrão). Configure a base pública somente se as imagens
   devam ser publicamente acessíveis por um CDN/domínio dedicado. Se o bucket
   continuar privado atrás do CDN, configure também o acesso de origem do CDN
   fora da aplicação, mantendo o bloqueio público do bucket.
5. Os testes usam cliente S3 falso; não exigem bucket, credenciais ou rede.
   Para validar a integração real, use um bucket de teste e credenciais
   temporárias com a mesma política mínima.

A configuração é validada na inicialização; provedor desconhecido, bucket S3
ausente, credenciais explícitas incompletas, URL inválida e valores numéricos
fora do formato/limite geram `ConfiguracaoStorageError` sem imprimir segredos.
