# Projeto de Engenharia de Software

Aplicação web em **Python + Flask** construída com **Clean Architecture**,
princípios **SOLID**, testes unitários com **pytest** e desenvolvimento
guiado por especificações (**Spec-Driven Development**).

> Trabalho 2 de Engenharia de Software: Arquitetura e Projeto de Software (PUC-Rio).

## Estrutura do projeto

A organização das camadas e o mapa de diretórios estão em
[ESTRUTURA.md](ESTRUTURA.md).

As dependências apontam para dentro: `app` e `infra` dependem de `use_cases`,
que dependem de `domain`. O `domain` não depende de nada externo.

## Modelagem do banco de dados

O schema SQLite e a documentação das tabelas estão em
[infra/db/README.md](infra/db/README.md). Sempre que dados persistidos forem
adicionados, alterados ou removidos, mantenha o schema, a documentação, os
testes e as migrações aplicáveis sincronizados.

## Armazenamento de imagens

A infraestrutura de imagens oferece os provedores `local` e `s3`, configurados
por variáveis de ambiente. O provedor local é o padrão para desenvolvimento e
testes; não existe outro provedor de armazenamento já adotado pelo projeto.
Copie os valores pertinentes de [`.env.example`](.env.example) para o ambiente
local. `init_storage(app)` combina as variáveis do ambiente com as chaves
`STORAGE_*` de `app.config`, cria o provedor e o registra em
`app.extensions["image_storage"]`. Configuração inválida interrompe a criação
do app. Não há carregador automático de arquivo `.env`.

| Variável | Padrão | Descrição |
|---|---|---|
| `STORAGE_PROVIDER` | `local` | Provedor: `local` ou `s3` |
| `STORAGE_MAX_IMAGE_BYTES` | `5242880` | Limite de imagem em bytes |
| `STORAGE_LOCAL_ROOT` | `media` | Diretório raiz do provedor local |
| `STORAGE_LOCAL_URL_BASE` | `/media` | Prefixo da rota e das URLs locais |
| `STORAGE_S3_BUCKET` | — | Obrigatório para o provedor S3 |
| `STORAGE_S3_REGION` | — | Região opcional do bucket |
| `STORAGE_S3_ENDPOINT_URL` | — | Endpoint opcional compatível com S3 |
| `STORAGE_S3_ACCESS_KEY_ID` | — | Chave opcional; deve acompanhar o segredo |
| `STORAGE_S3_SECRET_ACCESS_KEY` | — | Segredo opcional; deve acompanhar a chave |
| `STORAGE_S3_PUBLIC_BASE_URL` | — | Base pública opcional; sem ela usa URL pré-assinada |
| `STORAGE_S3_PRESIGN_EXPIRES_SECONDS` | `3600` | Validade da URL pré-assinada |
| `STORAGE_S3_KEY_PREFIX` | — | Prefixo opcional dentro do bucket |

### Desenvolvimento local

Com `STORAGE_PROVIDER=local` (ou sem definir a variável), nenhuma credencial é
necessária. A aplicação cria `media/` no projeto ao salvar a primeira imagem e
serve arquivos pela rota `/media/<chave>`. JPEG, PNG e WebP são aceitos até
5 MiB por padrão. O limite pode ser ajustado com `STORAGE_MAX_IMAGE_BYTES`.
O disco local **não é adequado a ambientes com sistema de arquivos efêmero**,
como contêineres recriados em cada deploy. Servir mídia local pelo Flask não é
recomendado em produção; use o provedor `s3` ou sirva a pasta de mídia pelo
servidor web/proxy.

## Autenticação temporária para a prévia

A rota `GET /anuncios/novo` consulta a porta `Autenticador` antes de renderizar
a página. `AutenticadorMock` é um **mock temporário**: por padrão não fornece
usuário e a rota redireciona para `/login`, que informa que o login real ainda
não está disponível. Não há sessão, credenciais, persistência de usuários nem
endpoint de login funcional.

Para testes ou desenvolvimento controlado, injete uma identidade fictícia ao
criar a aplicação:

```python
from app.main import create_app
from infra.repositories.autenticador_mock import AutenticadorMock
from use_cases.identidade_autenticada import UsuarioAutenticado

app = create_app(
    autenticador=AutenticadorMock(
        UsuarioAutenticado(
            id_usuario=1,
            nome_exibicao="Anunciante de teste",
        )
    )
)
```

Esse mock serve apenas para exercitar a identificação de um usuário e **não
deve ser usado em produção**. A autenticação real e a regra de perfil completo
da US02 continuam pendentes; esta prévia não implementa o critério de
completude nem a publicação pela API.

Para executar localmente, configure `STORAGE_PROVIDER=local` no ambiente
(opcional, pois é o padrão), instale as dependências com `make install` e inicie
a aplicação como descrito na seção [Executar a aplicação](#executar-a-aplicação).

### Configuração de bucket compatível com S3

1. Crie um bucket sem acesso público e mantenha bloqueado o acesso público
   (Block Public Access) por padrão.
2. Crie um usuário ou função de serviço dedicado à aplicação. Conceda somente
   as operações de objeto necessárias no bucket e prefixo utilizados; não
   conceda listagem nem administração do bucket.
3. Configure `STORAGE_PROVIDER=s3` e `STORAGE_S3_BUCKET`. `STORAGE_S3_REGION`
   e `STORAGE_S3_ENDPOINT_URL` são opcionais (o endpoint permite serviços
   compatíveis, como R2 ou MinIO).
4. Prefira a cadeia padrão de credenciais do boto3, como uma função IAM.
   Alternativamente configure **ambas** `STORAGE_S3_ACCESS_KEY_ID` e
   `STORAGE_S3_SECRET_ACCESS_KEY` no ambiente secreto do deploy. Nunca coloque
   credenciais reais no repositório.
5. Sem `STORAGE_S3_PUBLIC_BASE_URL`, o sistema gera URLs pré-assinadas de
   leitura, válidas por `STORAGE_S3_PRESIGN_EXPIRES_SECONDS` (padrão 3600).
   Configure uma base pública apenas se houver decisão explícita de servir
   imagens publicamente, idealmente por CDN ou domínio restrito ao prefixo de
   imagens. O bucket deve permanecer privado por padrão.
6. `STORAGE_S3_KEY_PREFIX` é opcional e restringe os objetos a um prefixo
   dentro do bucket.

Exemplo de política IAM mínima, substituindo região, conta, bucket e prefixo
pelos valores do ambiente:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["s3:PutObject", "s3:GetObject", "s3:DeleteObject"],
      "Resource": "arn:aws:s3:::SEU_BUCKET/anuncios/*"
    }
  ]
}
```

O banco e outros consumidores devem persistir **a chave** (por exemplo,
`anuncios/<uuid>.jpg`), nunca a URL completa. A URL é derivada em tempo de
leitura, permitindo trocar domínio, CDN ou provedor sem migrar dados. A camada
de storage valida o conteúdo pela assinatura, aceita apenas JPEG, PNG e WebP,
gera chaves próprias e trata arquivos como imutáveis. O endpoint de upload,
vínculo de imagens com anúncios e exibição no front-end são tarefas separadas.
O storage valida o tamanho do conteúdo, mas não define `MAX_CONTENT_LENGTH`
global. O futuro endpoint de upload deve impor seu próprio limite de requisição,
incluindo o overhead multipart além do máximo de 5 MiB por imagem.

## Pré-requisitos

- Python 3.11 ou superior
- Git
- GNU Make para os comandos `make`

## Como inicializar o ambiente

### 1. Clonar o repositório

```bash
git clone <url-do-repositorio>
cd projeto_engenharia_de_software
```

### 2. Criar o ambiente virtual

```bash
python -m venv .venv
```

### 3. Ativar o ambiente virtual

Windows (PowerShell):

```powershell
.venv\Scripts\Activate.ps1
```

> Se o PowerShell bloquear a execução do script, rode uma vez:
> `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`

Windows (Git Bash):

```bash
source .venv/Scripts/activate
```

Linux / macOS:

```bash
source .venv/bin/activate
```

### 4. Instalar as dependências

```bash
make install
```

## Executar a aplicação

```bash
flask --app app.main:create_app run --debug
```

A aplicação sobe em http://127.0.0.1:5000. Para conferir, acesse
http://127.0.0.1:5000/health, que deve responder `{"status": "ok"}`.

### Variáveis de ambiente

| Variável | Padrão | Uso |
|---|---|---|
| `JWT_SECRET` | temporário (gerado a cada início) | Segredo que assina os tokens de sessão. Obrigatório fora do desenvolvimento |
| `JWT_EXPIRA_MINUTOS` | `60` | Validade do token de sessão |
| `URL_LINK_MAGICO` | `http://localhost:5000/entrar/link` | Endereço do front que recebe `?token=` do link enviado por e-mail |
| `SMTP_HOST` | vazio | Servidor SMTP. Vazio: o e-mail é escrito no log em vez de enviado |
| `SMTP_PORT` | `587` | Porta SMTP |
| `SMTP_USUARIO` / `SMTP_SENHA` | vazio | Credenciais SMTP, se o servidor exigir |
| `SMTP_REMETENTE` | `nao-responda@localhost` | Remetente dos e-mails |
| `SMTP_STARTTLS` | `true` | Usa STARTTLS na conexão SMTP |

As rotas de autenticação (`/auth/...`) estão descritas em
[spec/features/001-autenticacao/plan.md](spec/features/001-autenticacao/plan.md).

### API de anúncios

`POST /api/ads` cria um anúncio para o usuário autenticado. Envie o JWT no
cabeçalho `Authorization: Bearer <token>` e um objeto JSON com `titulo`,
`categoria` e `descricao`. `estado_conservacao` é obrigatório para produtos e
deve ser omitido ou `null` para serviços e eventos. `preco_a_combinar` é
opcional e assume `false`; nesse caso, `preco` é obrigatório e aceita número
JSON ou string numérica. Quando `preco_a_combinar` for `true`, `preco` deve ser
omitido ou `null`. O corpo não pode definir `id`, `id_anunciante`,
`nome_anunciante`, `created_at` nem campos desconhecidos.

O preço é validado com `Decimal`, sem `float`; o corpo é limitado a 64 KiB.
Em sucesso, a resposta `201` contém o anúncio lido do banco após a inserção,
com `created_at` e `nome_anunciante`. `preco` é uma string com duas casas
decimais ou `null` para “a combinar”.

Exemplo de produto:

```json
{
  "titulo": "Bicicleta urbana",
  "categoria": "produto",
  "estado_conservacao": "usado_regular",
  "descricao": "Revisada e pronta para uso.",
  "preco": 850.00
}
```

Resposta `201`:

```json
{
  "id": 1,
  "id_anunciante": 1,
  "nome_anunciante": "Ana",
  "titulo": "Bicicleta urbana",
  "categoria": "produto",
  "estado_conservacao": "usado_regular",
  "descricao": "Revisada e pronta para uso.",
  "preco": "850.00",
  "preco_a_combinar": false,
  "created_at": "2026-11-16T14:00:00.000Z"
}
```

Exemplo de serviço “a combinar”:

```json
{
  "titulo": "Aulas de matemática",
  "categoria": "servico",
  "estado_conservacao": null,
  "descricao": "Aulas particulares.",
  "preco_a_combinar": true,
  "preco": null
}
```

Resposta `201`:

```json
{
  "id": 2,
  "id_anunciante": 1,
  "nome_anunciante": "Ana",
  "titulo": "Aulas de matemática",
  "categoria": "servico",
  "estado_conservacao": null,
  "descricao": "Aulas particulares.",
  "preco": null,
  "preco_a_combinar": true,
  "created_at": "2026-11-16T14:01:00.000Z"
}
```

Exemplo de evento gratuito:

```json
{
  "titulo": "Feira comunitária",
  "categoria": "evento",
  "descricao": "Evento aberto à comunidade.",
  "preco": 0
}
```

Resposta `201`:

```json
{
  "id": 3,
  "id_anunciante": 1,
  "nome_anunciante": "Ana",
  "titulo": "Feira comunitária",
  "categoria": "evento",
  "estado_conservacao": null,
  "descricao": "Evento aberto à comunidade.",
  "preco": "0.00",
  "preco_a_combinar": false,
  "created_at": "2026-11-16T14:02:00.000Z"
}
```

Os erros são JSON. `422` inclui um mapa `campos` com a mensagem de cada
campo inválido. Os demais códigos são:

| Status | Situação |
|---|---|
| `400` | JSON inválido ou corpo que não seja um objeto |
| `401` | Token ausente, inválido ou usuário não encontrado em `usuarios` |
| `403` | Perfil incompleto, com `codigo: "perfil_incompleto"` |
| `413` | Corpo maior que 64 KiB |
| `415` | Content-Type diferente de JSON |
| `500` | Falha inesperada; detalhes internos não são retornados |

O JWT é enviado como Bearer, não por cookie de sessão; por isso, a rota não
usa CSRF por cookie. O usuário autenticado precisa existir também em `usuarios`
para que a chave estrangeira do anúncio seja válida.

#### Mock temporário do perfil US02

**TEMPORÁRIO — não usar em produção.** A US02 ainda não persiste os dados do
perfil. Até isso existir, `VerificadorPerfilCompletoMock` considera o perfil
completo quando nome de exibição, foto, WhatsApp e e-mail têm valores não
vazios. O mock guarda esses dados apenas em memória, não valida se a foto
existe nem se o WhatsApp é válido. O `create_app` padrão não recebe perfis e,
portanto, bloqueia a publicação com `403` (fail-closed). Testes e ambientes
controlados podem injetar um perfil explicitamente:

```python
verificador = VerificadorPerfilCompletoMock(
    {
        1: PerfilAnuncianteMock(
            nome_exibicao="Ana",
            foto="mock://foto-temporaria",
            whatsapp="+5521999999999",
            email="ana@aluno.puc-rio.br",
        )
    }
)
app = create_app(verificador_perfil=verificador)
```

Quando a US02 for implementada, substitua esse adaptador por uma consulta aos
dados persistidos do perfil, mantendo o contrato `esta_completo(id_usuario)`.
A autenticação existente também usa repositório de usuários em memória; o
provisionamento persistente de contas permanece fora desta API.

O SQLite usa `instance/classificados.sqlite3` por padrão. A conexão é obtida
por requisição com `app.database.get_db`; `DATABASE` pode ser substituído na
configuração da aplicação, especialmente nos testes.

Para executar os testes:

```bash
make test
```

## Qualidade do código

Use o `Makefile` para executar o lint e/ou todas as verificações:

```bash
make lint
make check
```

`make check` é o alvo padrão e executa lint e testes. O Flake8 segue as regras
em `setup.cfg`. Para gerar cobertura:

```bash
python -m pytest --cov=domain --cov=use_cases --cov-report=term-missing
```

## Desenvolvimento guiado por especificações

Toda funcionalidade começa por uma especificação em `spec/features/`.
O fluxo (especificar → planejar → quebrar em tarefas → implementar → validar)
está descrito em [spec/README.md](spec/README.md), e os princípios do projeto
estão em [spec/constitution.md](spec/constitution.md).

## Requisitos do trabalho

- [ ] Pelo menos 4 histórias de usuário implementadas
- [ ] Pelo menos 2 entidades
- [ ] Organização segundo a Clean Architecture
- [ ] Princípios SOLID aplicados
- [ ] Testes unitários dos use cases, isolados da infraestrutura
- [ ] Código seguindo a PEP-8
- [ ] (Bônus) Uso de IA justificado e com boa estratégia
