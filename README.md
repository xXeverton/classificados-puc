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
local. A aplicação lê as variáveis do ambiente; não há carregador automático
de arquivo `.env`.

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
como contêineres recriados em cada deploy.

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
