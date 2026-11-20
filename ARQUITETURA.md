# Clean Architecture na API de Classificados

Este documento adapta a arquitetura de [ARQUITETURA.md](ARQUITETURA.md) ao
domínio de classificados universitários. A API fica em `server/`; o projeto de
interface `front/` é externo a este repositório.

## Estrutura de pastas

```text
server/
├── app.py                              # cria a API, configura CORS e monta dependências
├── requirements.txt                   # dependências da API e ferramentas Python
├── core/                               # regras de negócio sem Flask ou SQLAlchemy
│   ├── entities/
│   │   ├── usuario.py                 # Usuario (conta, confirmação e bloqueio de login)
│   │   ├── vinculo.py                 # Enum Vinculo (aluno, funcionário)
│   │   ├── token_de_confirmacao.py    # link de confirmação de uso único
│   │   ├── sessao.py                  # sessão autenticada
│   │   ├── senha.py                   # regra de tamanho mínimo da senha
│   │   └── politicas_autenticacao.py  # prazos, limites e hash de tokens
│   ├── interfaces/                    # contratos: repositórios, e-mail, hash, token, relógio
│   └── usecases/
│       ├── erros.py                   # erros de aplicação sem códigos HTTP
│       ├── cadastrar_usuario.py       # um arquivo por caso de uso
│       ├── emissor_de_confirmacao.py  # colaborador que emite e envia o link
│       └── ...                        # confirmar, reenviar, autenticar, sessão
├── infra/                              # adaptadores técnicos
│   ├── db/
│   │   ├── database.py                # engine, Session, pragma de FKs e criação das tabelas
│   │   ├── models.py                  # modelos SQLAlchemy
│   │   ├── schema.sql                 # schema SQLite de referência
│   │   └── README.md                  # documentação do modelo persistido
│   ├── gateways/                      # repositórios SQLAlchemy
│   └── services/                      # e-mail (log/SMTP), hash de senha, tokens, relógio
└── api/                                # entrada e saída HTTP
    ├── autenticacao.py                # decorator exige_sessao (Bearer token)
    ├── erros_http.py                  # erros do core → status HTTP
    ├── controllers/
    │   ├── health_controller.py       # GET /health
    │   └── auth_controller.py         # rotas /auth/*
    └── presenters/                    # schemas de saída e presenters

tests/                                  # testes organizados pelos adaptadores/camadas
├── api/
├── core/
│   ├── entities/
│   └── usecases/                      # fakes.py: dublês em memória
└── infra/
    ├── db/
    ├── gateways/
    └── services/

spec/                                   # especificações, planos e tarefas SDD
.github/skills/                         # skills do projeto
Makefile                                # instalação, lint e testes
README.md                               # guia principal
setup.cfg                               # configuração de pytest e Flake8
```

O controller de saúde preserva o endpoint existente `GET /health`. A
autenticação (feature 001) está em `/auth/*`. Os casos de uso de perfil e
anúncios devem ser acrescentados a `core/` quando suas especificações e
decisões pendentes estiverem definidas.

### Rotas protegidas

Todo conteúdo da plataforma exige sessão de uma conta confirmada (RN6 da
feature 001). **Toda rota de conteúdo (feed, anúncios, eventos etc.) deve usar
o decorator `exige_sessao`** de `server/api/autenticacao.py`, que responde
`401` sem um `Authorization: Bearer <token>` válido e deixa o usuário logado
em `flask.g.usuario`. O controller o recebe já montado com o caso de uso
`ObterUsuarioDaSessao`, como em `auth_controller.py`:

```python
protegida = exige_sessao(casos_de_uso.obter_usuario_da_sessao)

@blueprint.get("/feed", security=SEGURANCA_BEARER)
@protegida
def feed():
    ...
```

Só ficam públicas `/health` e as rotas de cadastro, confirmação, reenvio do
link e login.

### Correspondência com o diagrama

| Camada do diagrama | Diretório |
|---|---|
| Entities | `server/core/entities/` |
| Use Cases | `server/core/usecases/` + `server/core/interfaces/` |
| Controllers, Presenters | `server/api/controllers/`, `server/api/presenters/` |
| Gateways | `server/infra/gateways/` |
| DB | `server/infra/db/` (SQLAlchemy + SQLite) |
| Web | Flask-OpenAPI3 e CORS, configurados em `server/app.py` |
| UI | `front/` (fora da API e não incluído neste repositório) |
| Devices, External Interfaces | não há integração implementada atualmente |

## Diagrama de dependências

As setas indicam **quem importa quem**. As dependências de negócio apontam
para dentro, em direção ao `core`; o `core` não importa `api/` nem `infra/`.
`server/app.py` é o único ponto de montagem que conhece os adaptadores
concretos.

```mermaid
flowchart TB
    UI["front/ (UI, externo)"]

    subgraph API["server/api/"]
        CTRL["controllers<br/>rotas + schemas de entrada"]
        PRES["presenters<br/>presenters + schemas de saída"]
    end

    subgraph CORE["server/core/"]
        UC["usecases<br/>operações de negócio"]
        IF["interfaces<br/>UsuarioRepositoryInterface"]
        ENT["entities<br/>Usuario"]
    end

    subgraph INFRA["server/infra/"]
        GW["gateways<br/>UsuarioRepositorySQLAlchemy"]
        DB["db<br/>database.py / models.py"]
    end

    APP["server/app.py<br/>Flask-OpenAPI3 + CORS + montagem"]
    SQLITE[("SQLite<br/>server/database/db.sqlite3")]

    UI -- "HTTP / JSON" --> CTRL
    CTRL --> UC
    CTRL --> PRES
    PRES --> ENT
    UC --> IF
    UC --> ENT
    IF --> ENT
    GW -. "implementa" .-> IF
    GW --> ENT
    GW --> DB
    DB --> SQLITE
    APP --> CTRL
    APP --> GW

    classDef entities fill:#fbf6b6,stroke:#333,color:#000
    classDef usecases fill:#f6a5a5,stroke:#333,color:#000
    classDef adapters fill:#a7f3b5,stroke:#333,color:#000
    classDef frameworks fill:#a6d8f7,stroke:#333,color:#000

    class ENT entities
    class UC,IF usecases
    class CTRL,PRES,GW adapters
    class DB,SQLITE,UI,APP frameworks
```

`server/app.py` cria o repositório concreto e o disponibiliza para a camada
de casos de uso quando eles forem montados. A interface define o contrato sem
saber que a implementação usa SQLAlchemy.

## Fluxo de uma requisição

O fluxo abaixo é genérico: não define uma rota de negócio que ainda não esteja
especificada.

```mermaid
sequenceDiagram
    participant F as front (UI)
    participant C as Controller<br/>server/api/controllers
    participant U as Caso de uso<br/>server/core/usecases
    participant R as Gateway<br/>server/infra/gateways
    participant P as Presenter<br/>server/api/presenters

    F->>C: Requisição HTTP / JSON
    C->>C: Validar estrutura da entrada
    C->>U: Executar com dados validados
    U->>R: Consultar ou persistir pela interface
    R-->>U: Entidade ou resultado
    U-->>C: Resultado do caso de uso
    C->>P: Apresentar resultado
    P-->>C: Schema de saída
    C-->>F: Resposta HTTP / JSON
```

Se uma regra de negócio falhar, o caso de uso produz um erro independente de
HTTP e o controller/presenter o converte em resposta. Assim, o `core` não
conhece códigos de status.

## Schemas: entrada com o controller, saída com o presenter

Os schemas Pydantic descrevem a forma dos dados, sem substituir regras de
negócio:

- **Schemas de entrada** ficam em `api/controllers/`, junto ao controller que
  os valida antes de chamar o caso de uso.
- **Entidades**, como `Usuario`, pertencem a `core/entities/`; não são modelos
  SQLAlchemy nem respostas HTTP.
- **Schemas de saída** ficam em `api/presenters/`. O presenter cria o modelo
  de resposta a partir da entidade ou do resultado do caso de uso.
- **`ErrorSchema`** fica no presenter de erros. O controller converte erros
  conhecidos em respostas HTTP; casos de uso não importam schemas HTTP.
- Campos pessoais só podem aparecer em respostas conforme a regra de
  visibilidade aprovada para o perfil.

## Regras de domínio: autenticação e perfil

A épica [PROJ-8](https://matheuscomputacaopuc.atlassian.net/browse/PROJ-8)
é detalhada pelas histórias
[PROJ-1 — Logar com validação institucional](https://matheuscomputacaopuc.atlassian.net/browse/PROJ-1)
e
[PROJ-4 — Completar perfil de anunciante](https://matheuscomputacaopuc.atlassian.net/browse/PROJ-4).
Estas regras pertencem ao `core`; controllers e banco não devem ser a única
camada que as aplica.

### Autenticação institucional

- O público elegível é composto por alunos e funcionários; terceirizados estão
  fora do escopo atual. Uma conta nova só pode ser criada para pessoa com um
  desses vínculos.
- O grupo adotou o plano B: a plataforma é restrita a e-mails institucionais
  da PUC-Rio (`@puc-rio.br` e `@aluno.puc-rio.br`), confirmados por um link
  enviado ao e-mail. Detalhes em
  `spec/features/001-cadastro-login-verificacao-email/`.
- O login usa um único campo, que aceita e-mail, nome de usuário ou
  matrícula (opcional no cadastro), e a senha.
- Credenciais inválidas produzem a mensagem `Credenciais inválidas`, sem
  indicar qual dado está errado. Após cinco tentativas erradas consecutivas,
  o login da conta fica bloqueado por dez minutos.
- Senhas devem ser armazenadas com hash seguro, nunca em texto puro nem por
  criptografia reversível.

### Perfil de anunciante

- O perfil inclui nome de exibição, foto opcional, WhatsApp e e-mail de contato.
- O vínculo de aluno ou funcionário vem do cadastro, aparece no perfil e não
  pode ser editado pelo fluxo de perfil.
- O perfil está completo quando tem nome de exibição e pelo menos uma forma de
  contato (WhatsApp ou e-mail). A publicação exige perfil completo; a regra
  pertence ao caso de uso de publicação.
- Foto acima de 2 MB ou em formato não aceito deve ser rejeitada sem salvar
  essa foto; ela pode ser omitida. Os formatos aceitos ainda precisam ser
  definidos.
- A visibilidade do perfil para compradores ainda consta como pendência na
  Definition of Ready de PROJ-4. Até essa decisão, não presuma que e-mail,
  WhatsApp, matrícula ou outros dados sejam públicos.

## Persistência e testes

O modelo SQLite atual contém as tabelas `usuarios`, `tokens_confirmacao` e
`sessoes`, documentadas em `server/infra/db/README.md`. Os modelos
SQLAlchemy mantêm as mesmas colunas e constraints do `schema.sql`.
`create_all` cria tabelas ausentes, mas não atualiza tabelas já existentes;
mudanças incompatíveis exigem migração explícita.

- Testes de entidades ficam em `tests/core/entities/`.
- Testes de casos de uso ficam em `tests/core/usecases/` e usam repositórios
  falsos em memória.
- Testes dos gateways e do schema ficam em `tests/infra/`.
- Testes dos controllers e presenters ficam em `tests/api/`.
- Toda mudança persistida sincroniza modelos SQLAlchemy, `schema.sql`,
  documentação e testes.
