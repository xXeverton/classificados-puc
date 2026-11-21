# Registro de decisões do projeto

Decisões gerais que valem para **todas** as features. Consulte este arquivo
antes de escrever uma spec ou um plano: o que está aqui já foi decidido e não
precisa ser perguntado de novo.

- A `constitution.md` traz os princípios de código (Clean Architecture, SOLID,
  testes, estilo). Este arquivo traz as **decisões de produto e técnicas**
  tomadas ao longo das features.
- Cada decisão tem um ID (`D-NNN`). Specs e planos citam o ID em vez de copiar
  o texto.
- Quando uma dúvida de uma spec for respondida e valer para o projeto todo,
  registre aqui. Decisões que só valem para uma feature ficam na própria spec.
- Não apague decisões: se uma mudar, marque a antiga como
  **Substituída por D-NNN** e crie a nova.

## Produto e acesso

| ID | Decisão | Origem |
|---|---|---|
| D-001 | A plataforma é **restrita a pessoas com e-mail institucional da PUC-Rio** (`@puc-rio.br` e `@aluno.puc-rio.br`). Não há acesso de pessoas externas. Essa restrição substitui, no MVP, a moderação de conteúdo como mecanismo de confiança. | Spec 001 |
| D-002 | A conta só é liberada depois da **confirmação do e-mail** por um link de 15 minutos e uso único. A confirmação exige um clique na página (abrir o link sozinho não confirma), porque filtros de e-mail da universidade abrem links automaticamente. | Specs 001 e 002 |
| D-003 | O **e-mail é o identificador principal** da conta. Nome de usuário (obrigatório, sem `@`) e matrícula (opcional, não conferida) são identificadores alternativos, únicos entre si. O login usa um único campo que aceita qualquer um dos três. | Spec 001 |
| D-004 | **Todo conteúdo exige login** com conta confirmada, inclusive arquivos como fotos de perfil. Não há acesso anônimo. Só são públicas as rotas de saúde, cadastro, confirmação, reenvio do link e login. | Specs 001 e 003 |
| D-005 | O **vínculo** é aluno ou funcionário, informado no cadastro e **não editável** depois. Terceirizados e outros vínculos estão fora do escopo. | Spec 001 |
| D-006 | Senha com **no mínimo 8 caracteres**, guardada só como hash. Após **5 falhas seguidas**, o login da conta fica bloqueado por **10 minutos**. Falhas de login mostram só "Credenciais inválidas". | Spec 001 |
| D-007 | **Sem papéis, permissões diferenciadas nem moderação** no MVP: todos os membros confirmados têm o mesmo acesso. | Spec 001 |

## Perfil e contatos

| ID | Decisão | Origem |
|---|---|---|
| D-010 | Todo membro tem um **perfil comum**, criado no cadastro (nome, e-mail, nome de usuário, matrícula, vínculo). O **perfil de anunciante** é uma extensão opcional, escolhida pela pessoa na tela do próprio perfil. Só existe perfil de anunciante completo (nome de exibição + ao menos um contato, ver D-013), e **tê-lo é a condição para publicar anúncios**. | Spec 003 |
| D-011 | **Substituída por D-013.** Previa só WhatsApp (número ou link) e um e-mail de contato como campos fixos do perfil. | Spec 003 |
| D-012 | **Foto de perfil**: opcional, JPG, PNG ou WEBP de até 2 MB, com o formato conferido pelo conteúdo do arquivo. Novas features com imagens (ex.: anúncios) partem desta regra e confirmam na própria spec se ela vale. | Spec 003 |
| D-013 | **Contatos do anunciante** são uma **lista** (ao menos 1, no máximo 10, na ordem definida pela pessoa) de contatos com tipo e valor: **WhatsApp** (por número, com código do país escolhido numa lista, padrão Brasil +55, ou por link de conversa `wa.me`/`api.whatsapp.com`, que vale mesmo sem número), **telefone** (código do país + número, mesma regra de 8 a 15 dígitos), **e-mail** (qualquer domínio), **site** (`https://`) e **link** (`https://`, com rótulo opcional). Pode haver vários do mesmo tipo, sem repetir tipo e valor. Rótulo de link com até 40 caracteres e endereços com até 2048. Novas features que mostrem contatos reutilizam essa lista. | Spec 003 |

## API e backend

| ID | Decisão | Origem |
|---|---|---|
| D-020 | **Rotas** sem prefixo `/api`, em português e em `kebab-case`, agrupadas por recurso (ex.: `/auth/login`, `/perfil-anunciante`). Recursos do usuário logado não levam id na URL (ex.: `/auth/me`): o usuário vem da sessão. Se o Jira citar outra rota, vale o padrão do projeto. | Specs 001 e 003 |
| D-021 | **Sessão** por token opaco no header `Authorization: Bearer`; o banco guarda só o hash SHA-256. Logout revoga a sessão no servidor. Toda rota de conteúdo usa o decorator `exige_sessao`. | Spec 001 |
| D-022 | **Erros da API** em JSON com mensagem e, quando o front precisa reagir de forma específica, um `codigo` (ex.: `email_nao_confirmado`). O core gera erros sem HTTP; `server/api/erros_http.py` faz a tradução para status. | Spec 001 |
| D-023 | **Datas em UTC**, com o relógio injetado nos casos de uso para testar prazos sem esperar. | Spec 001 |
| D-024 | **Envio de e-mail**: em desenvolvimento e testes o e-mail aparece no log (`EMAIL_BACKEND=log`); nos demais ambientes vai por SMTP configurado por variáveis de ambiente. Segredos nunca entram no repositório. | Spec 001 |
| D-025 | **Arquivos enviados** (ex.: fotos) passam por uma interface no core e, por enquanto, ficam em disco local em `server/uploads/` (fora do git), com nome aleatório. São servidos só com sessão (D-004); o front baixa com o token e mostra a imagem por um endereço `blob:`. | Spec 003 |

## Front-end

| ID | Decisão | Origem |
|---|---|---|
| D-030 | O front fica em `front/`, com **HTML, CSS e JavaScript puros** (módulos ES), sem framework, sem build e sem dependências de npm. Uma pasta por tela com `index.html`. Testes com `node --test` nos módulos sem DOM; telas por roteiro manual. | Spec 002 |
| D-031 | Dados de usuário ou da API são exibidos só como texto: **proibido `innerHTML`**. A senha nunca fica na tela depois de uma falha nem é guardada no navegador. | Spec 002 |
| D-032 | **Visual e comportamento comuns**: todas as telas usam `front/css/tema.css` e os componentes de `front/guia-de-estilo/`. **Sem wireframe**, a tela nova segue esse tema e esse guia. Toda tela segue o comportamento geral da spec 002 (CA23 a CA28): botão indisponível durante o envio, aviso de falha de conexão sem perder o que foi preenchido, uso pelo teclado com rótulos e erros junto aos campos, celular sem rolagem horizontal. | Specs 002 e 003 |
| D-033 | **Mensagens**: erros vindos do servidor mostram o texto que a API devolve; validações locais e avisos próprios da tela ficam em `front/js/dominio/mensagens.js`. As telas conferem antes de enviar só as regras que não dependem de outras contas; o servidor é a fonte da verdade. | Spec 002 |
| D-034 | **Sempre seguir o guia de estilo** (`front/guia-de-estilo/` e `front/css/tema.css`), em toda tela nova ou alterada, por quem implementa, inclusive agentes de IA. Usar as variáveis de `:root`, nunca cores ou medidas soltas, e os componentes existentes (`painel`, `formulario`, `campo`, `botao`, `alerta`, `opcoes`, `etiqueta`…) antes de criar classes novas. Estilo específico de uma tela vai em um CSS próprio dela (por exemplo `front/css/perfil.css`), **nunca dentro do `tema.css`**. Um componente que serve a várias telas entra no `tema.css` **e** no guia de estilo. Em dúvida, abrir `/guia-de-estilo/` e comparar com a tela. | Spec 003 (pedido do time) |

## Dados

| ID | Decisão | Origem |
|---|---|---|
| D-040 | **SQLite com SQLAlchemy.** Toda tabela tem `id` inteiro como chave primária técnica; chaves de negócio (como o e-mail) são `UNIQUE`. Chaves estrangeiras se chamam `<entidade>_id`. | Spec 001 |
| D-041 | Os **nomes de tabelas e colunas** seguem o padrão do projeto, mesmo que o Jira use outro (ex.: `usuario_id` em vez de `id_usuario`). O mapeamento fica registrado no `server/infra/db/README.md`. | Spec 003 |
| D-042 | Identificadores comparados sem diferenciar maiúsculas (e-mail, nome de usuário, matrícula) são **gravados normalizados** em minúsculas e sem espaços nas pontas. | Spec 001 |
| D-043 | **Migração**: enquanto só existirem bancos locais de desenvolvimento, não há script de migração. Mudança incompatível em tabela existente → apagar `server/database/db.sqlite3` e deixar recriar (documentado no README). Tabela nova não exige nada. Modelos, `schema.sql`, README do banco e testes mudam juntos (skill `manter-modelagem-dados`). | Specs 001 e 003 |

## Processo

| ID | Decisão | Origem |
|---|---|---|
| D-050 | **Uma spec por história do Jira.** O `tasks.md` separa os blocos por subtarefa, na ordem combinada com o time. | Spec 003 |
| D-051 | Uma spec só passa a **Aprovada** com confirmação explícita, e nenhum código é escrito antes disso. | `spec/README.md` |

## Pendências gerais

Decisões que afetam mais de uma feature e ainda não foram tomadas.

| ID | Pendência | Onde decidir |
|---|---|---|
| P-001 | Quais dados do perfil de anunciante aparecem para os compradores, e onde (cartão do anúncio, página do anúncio, página do anunciante). | Feature de anúncios |
| P-002 | Onde publicar o front e a API para outras pessoas testarem (o link de confirmação hoje aponta para `localhost`). | A definir |
