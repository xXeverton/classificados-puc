# Plano técnico: Perfil de anunciante

Referência: `spec.md` desta pasta (CA1–CA31, RN1–RN13). Decisões gerais do
projeto: [`spec/decisoes.md`](../../decisoes.md).

## Decisões técnicas

| Tema | Decisão | Motivo |
|---|---|---|
| Perfil comum | Não muda nada no banco: o perfil comum é a própria tabela `usuarios`, já exposta por `GET /auth/me`. | RN1: o perfil comum vem do cadastro. |
| Perfil de anunciante | Entidade `Anunciante`, tabela `anunciantes`, relação 1:1 opcional com `usuarios`. Não há coluna "completo": ter linha em `anunciantes` = ser anunciante, e o gateway só grava perfis válidos (nome e ao menos um contato). | RN3 e D-010. Evita um campo derivado que pode ficar inconsistente. |
| Contatos | Tabela filha `contatos_anunciante` (uma linha por contato), com `tipo`, `codigo_pais`, `valor`, `rotulo` e `posicao`. A entidade `Anunciante` tem `contatos: tuple[Contato, ...]`. | RN4, RN5 e D-013: vários contatos, de tipos diferentes e até do mesmo tipo, em ordem definida pela pessoa. Colunas fixas por tipo não comportam "dois links". |
| Representação do contato | `tipo` (`whatsapp`, `telefone`, `email`, `site`, `link`); `valor` guarda o número só com dígitos (WhatsApp por número e telefone), o link (WhatsApp por link, site e link) ou o e-mail; `codigo_pais` só existe em número de WhatsApp e em telefone (em WhatsApp, `codigo_pais` vazio significa "por link"); `rotulo` só em link. | Uma única forma de gravar cada tipo; o código do país fica separado para a tela mostrá-lo selecionado ao editar (códigos têm 1 a 3 dígitos e não dá para separá-los depois). |
| Substituição | Salvar o perfil **substitui a lista inteira** de contatos, na mesma transação do restante do perfil. | RN8 (tudo ou nada) e CA9/CA20: a tela envia a lista final. |
| Nomes das colunas | `usuario_id` (a PROJ-25 diz `id_usuario`) e `nome_exibicao` (a PROJ-25 diz `nome`). Os contatos da PROJ-25 (`whatsapp`, `email_contato`) viram linhas de `contatos_anunciante`. | D-040 e D-041: padrão das chaves estrangeiras existentes; `nome_exibicao` evita confusão com `usuarios.nome`. |
| Lista de países | Fica no front (`front/js/dominio/codigos_paises.js`: nome do país, sigla e código), com o Brasil (+55) como padrão. O backend só confere que o código tem de 1 a 3 dígitos e que código + número somam de 8 a 15 dígitos. | A lista serve à tela; a regra de tamanho (padrão internacional E.164) é a que importa para o dado. |
| Endereços (site e link) | Só `https://`, com host contendo ponto, sem espaços e sem usuário/senha no endereço (`https://x@evil.com`). Links de WhatsApp: host exatamente `wa.me` ou `api.whatsapp.com`, sem porta nem usuário, com algo no caminho. | RN4. Impede guardar `javascript:`, `http://` ou endereços que enganam quem clica e que depois seriam mostrados aos compradores. |
| Foto | O core recebe os bytes e confere tamanho e formato pela **assinatura do arquivo** (JPEG `FF D8 FF`, PNG `89 50 4E 47 0D 0A 1A 0A`, WEBP `RIFF....WEBP`). Sem dependência nova (sem Pillow). | RN6: o formato vem do conteúdo, não do nome. |
| Armazenamento da foto | Interface `ArmazenamentoDeFotoInterface` no core; implementação em disco local (`FOTOS_PERFIL_DIR`, padrão `server/uploads/fotos_perfil/`, fora do git). Nome do arquivo: `secrets.token_urlsafe(32)` + extensão. `foto_url` guarda o caminho relativo `/fotos-perfil/<arquivo>`. | D-025. Trocar depois por um serviço de arquivos é só uma nova implementação. |
| Acesso à foto | `GET /fotos-perfil/<arquivo>` **exige sessão**. O front baixa a foto com `fetch` e o header `Authorization`, cria um `blob:` com `URL.createObjectURL` e o usa no `<img>`. | RN10 e D-004: login obrigatório para todo conteúdo. Uma tag `<img src>` comum não envia o token. |
| Tamanho da requisição | `MAX_CONTENT_LENGTH` do Flask em 3 MB (foto de 2 MB + campos). Acima disso o Flask responde `413` antes de ler tudo. | Evita carregar arquivos enormes na memória. A regra de 2 MB continua no core. |
| Envio dos contatos | `multipart/form-data` (por causa da foto) com o campo `contatos` contendo uma **lista em JSON** de `{tipo, codigo_pais, valor, rotulo}`. JSON malformado responde `400` `dados_invalidos`. | Uma requisição só para foto e contatos, mantendo o "tudo ou nada". |
| Rotas | `GET` e `PUT /perfil-anunciante`, sempre do usuário da sessão, e `GET /fotos-perfil/<arquivo>`. A PROJ-28 cita `PUT /api/users/profile`; fica no padrão do projeto. | D-020. Sem id na URL, não há como editar o perfil de outra pessoa (CA31). |
| Atomicidade (RN8) | O caso de uso valida tudo (foto e contatos) antes de gravar. A foto nova é gravada antes do perfil; se a gravação do perfil falhar, a foto nova é apagada. A foto antiga só é apagada depois que o perfil novo foi salvo. | Nunca deixar o perfil apontando para uma foto que não existe. |
| Volta ao anúncio (CA28) | O formulário recebe `?depois=anunciar`. O front só aceita valores de uma lista fixa (`anunciar` → `/anuncios/novo/`) e ignora o resto. | Evita redirecionamento para endereços arbitrários (open redirect). |
| Limites de segurança | Rótulo de link: 40 caracteres. Endereço de site ou link: 2048. Contatos: 10 (RN5). Constantes em `politicas_perfil.py`. | RN13: confirmados pelo time em 2026-11-20; ajustáveis num só lugar. |

### Configuração (variáveis de ambiente)

| Variável | Padrão | Uso |
|---|---|---|
| `FOTOS_PERFIL_DIR` | `server/uploads/fotos_perfil` | Pasta onde as fotos são gravadas |

## Entities (`server/core/entities/`)

| Entidade | Atributos | Regras/validações |
|----------|-----------|-------------------|
| `TipoDeContato` (nova, `Enum`) | `WHATSAPP = "whatsapp"`, `TELEFONE = "telefone"`, `EMAIL = "email"`, `SITE = "site"`, `LINK = "link"` | Valor fora da lista gera erro (CA11). |
| `Contato` (nova, objeto de valor imutável) | `tipo: TipoDeContato`, `valor: str`, `codigo_pais: str \| None`, `rotulo: str \| None` | Fábrica `Contato.criar(tipo, valor, codigo_pais=None, rotulo=None)` que normaliza por tipo: números só com dígitos (remove `+`, espaços, parênteses, hífens e pontos); e-mail em minúsculas; espaços das pontas removidos. Regras: **WhatsApp** com `codigo_pais` é número (1 a 3 dígitos de código, total de 8 a 15) e sem `codigo_pais` é link (`wa.me` ou `api.whatsapp.com`); **telefone** exige `codigo_pais` e a mesma regra de dígitos; **e-mail** com formato válido, qualquer domínio; **site** e **link** só `https://`; `codigo_pais` só em WhatsApp e telefone; `rotulo` só em link, até 40 caracteres, vazio vira `None`. Método `link_de_conversa()` (só WhatsApp): `https://wa.me/<código><número>` ou o próprio link. (CA11–CA18) |
| `Anunciante` (nova, `dataclass(frozen=True)`) | `usuario_id: int`, `nome_exibicao: str`, `contatos: tuple[Contato, ...]`, `foto_url: str \| None`, `id: int \| None` | Remove espaços do nome; vazio vira `None` na foto. Nome obrigatório (CA7). De 1 a 10 contatos (CA8, CA21). Sem contatos repetidos, ou seja, mesmo tipo, `codigo_pais` e valor (CA22). Aceita lista e guarda tupla. Métodos `com_foto(url)` e `sem_foto()`. |
| `FotoDePerfil` (nova, objeto de valor) | `conteudo: bytes`, `formato: FormatoDeFoto` | `FotoDePerfil.de_bytes(conteudo)` recusa vazio, acima de 2 MB ou assinatura desconhecida (CA23, CA24). |
| `FormatoDeFoto` (nova, `Enum`) | `JPEG = "jpg"`, `PNG = "png"`, `WEBP = "webp"` | O valor é a extensão usada no arquivo. |

Constantes em `politicas_perfil.py`: `TAMANHO_MAXIMO_FOTO_BYTES = 2 * 1024 *
1024`, `MINIMO_DIGITOS_TELEFONE = 8`, `MAXIMO_DIGITOS_TELEFONE = 15`,
`MAXIMO_DIGITOS_CODIGO_PAIS = 3`, `HOSTS_LINK_WHATSAPP = ("wa.me",
"api.whatsapp.com")`, `MAXIMO_CONTATOS = 10`, `MAXIMO_CARACTERES_ROTULO = 40`,
`MAXIMO_CARACTERES_ENDERECO = 2048`.

A validação do e-mail é uma expressão simples (`algo@dominio.tld`, sem
espaços). A validação institucional de `Usuario` **não** é reaproveitada.

## Use cases (`server/core/usecases/`)

| Use case | Entrada | Saída | Erros possíveis |
|----------|---------|-------|-----------------|
| `ObterPerfilAnunciante` | `usuario_id` | `Anunciante` | `PerfilNaoEncontrado` (CA2, CA27) |
| `SalvarPerfilAnunciante` | `usuario_id`, `nome_exibicao`, `contatos: list[DadosDeContato]`, `foto: bytes \| None`, `remover_foto: bool` | `Anunciante` salvo | `DadosInvalidos` (CA7, CA8, CA11, CA15–CA17, CA21, CA22), `FotoInvalida` (CA24) |

`DadosDeContato` é uma `dataclass` simples (`tipo`, `valor`, `codigo_pais`,
`rotulo`, todos em texto) definida junto ao caso de uso, para o controller não
conhecer as entidades.

Fluxo de `SalvarPerfilAnunciante` (RN8):

1. Se veio `foto`, monta `FotoDePerfil.de_bytes` (gera `FotoInvalida`).
2. Converte cada `DadosDeContato` com `Contato.criar`. Erros viram
   `DadosInvalidos`, dizendo qual contato (posição) falhou.
3. Busca o perfil atual (pode não existir) e monta o novo `Anunciante`,
   mantendo `foto_url` atual se não veio foto nem `remover_foto` (CA26). Erros
   da entidade viram `DadosInvalidos`.
4. Se veio foto, grava no armazenamento e usa a nova `foto_url`.
5. Salva o perfil (com a lista inteira de contatos). Se falhar, apaga a foto
   nova e repassa o erro.
6. Se a foto mudou ou foi removida, apaga a antiga.

O vínculo e os demais dados do perfil comum (CA1, CA10) não são dados do
anunciante: o front os lê de `GET /auth/me`.

Erros novos em `server/core/usecases/erros.py`, herdando de `ErroDeCasoDeUso`:
`PerfilNaoEncontrado` e `FotoInvalida`. `DadosInvalidos` já existe.

### Interfaces (`server/core/interfaces/`)

- `AnuncianteRepositoryInterface`: `buscar_por_usuario_id(usuario_id)`,
  `salvar(anunciante) -> Anunciante` (cria ou atualiza pelo `usuario_id`,
  substituindo a lista de contatos).
- `ArmazenamentoDeFotoInterface`: `salvar(foto: FotoDePerfil) -> str` (devolve
  a `foto_url`), `ler(foto_url) -> bytes | None`, `remover(foto_url)`.

## Infra (`server/infra/`) — PROJ-25 e skill `manter-modelagem-dados`

### Tabela `anunciantes` (nova)

| Coluna | Tipo | Obrigatória | Restrições |
|---|---|---:|---|
| `id` | INTEGER | Sim | PK, autoincremento |
| `usuario_id` | INTEGER | Sim | `UNIQUE`; FK → `usuarios.id`, `ON DELETE CASCADE` |
| `nome_exibicao` | TEXT | Sim | não vazio |
| `foto_url` | TEXT | Não | não vazio se informado |

### Tabela `contatos_anunciante` (nova)

| Coluna | Tipo | Obrigatória | Restrições |
|---|---|---:|---|
| `id` | INTEGER | Sim | PK, autoincremento |
| `anunciante_id` | INTEGER | Sim | FK → `anunciantes.id`, `ON DELETE CASCADE` |
| `posicao` | INTEGER | Sim | `>= 0`; `UNIQUE (anunciante_id, posicao)` |
| `tipo` | TEXT | Sim | `whatsapp`, `telefone`, `email`, `site` ou `link` |
| `codigo_pais` | TEXT | Não | obrigatório em `telefone`, opcional em `whatsapp` (vazio = link), proibido nos demais; só dígitos, 1 a 3 |
| `valor` | TEXT | Sim | não vazio; com `codigo_pais`, só dígitos e código + número somam 8 a 15 |
| `rotulo` | TEXT | Não | só em `link`; não vazio se informado |

Restrições por tipo (todas `CHECK`): `whatsapp` sem `codigo_pais` exige `valor`
começando com `https://wa.me/` ou `https://api.whatsapp.com/`, com algo depois
e sem espaços; `email` exige `@` depois do primeiro caractere; `site` e `link`
exigem `https://` e não têm espaços.

**O que o banco não garante:** o mínimo de 1 e o máximo de 10 contatos, a
ausência de contatos repetidos e o formato completo do e-mail. Isso fica nas
entidades `Anunciante` e `Contato`, e o gateway grava anunciante e contatos
numa única transação.

### Migração

São duas tabelas novas, sem alterar `usuarios`: `create_all` as cria em bancos
novos **e** existentes. Não é preciso apagar o banco local nem escrever script
de migração (D-043). O banco local atual não tem a tabela `anunciantes`,
conferido em 2026-11-20.

### Arquivos

- `server/infra/db/models.py`: `AnuncianteModel` e `ContatoAnuncianteModel`.
- `server/infra/db/schema.sql` e `server/infra/db/README.md` (diagrama com
  `Usuario "1" --> "0..1" Anunciante` e `Anunciante "1" --> "0..10"
  ContatoAnunciante`, tabelas de colunas, mapeamento de nomes da PROJ-25).
- `server/infra/gateways/anunciante_repository_sqlalchemy.py` (converte
  linhas de contato em `Contato` e vice-versa; contatos lidos por `posicao`).
- `server/infra/services/armazenamento_foto_local.py`.
- `.gitignore`: `server/uploads/`.

## Interface web (`server/api/controllers/`) — PROJ-28

Novo `perfil_anunciante_controller.py`, registrado em `server/app.py`, com
presenter `anunciante_presenter.py`.

| Método | Rota | Use case chamado | Resposta |
|--------|------|------------------|----------|
| GET | `/perfil-anunciante` | `ObterPerfilAnunciante` | `200` `{nome_exibicao, contatos: [{tipo, codigo_pais, valor, rotulo, link_de_conversa}], foto_url}` (`link_de_conversa` só em WhatsApp, `null` nos outros); `404` código `perfil_nao_encontrado`; `401` sem sessão |
| PUT | `/perfil-anunciante` | `SalvarPerfilAnunciante` | `multipart/form-data` com `nome_exibicao`, `contatos` (JSON), `foto` (arquivo) e `remover_foto`. `200` perfil salvo; `400` com código `dados_invalidos` ou `foto_invalida`; `413` acima de 3 MB; `401` sem sessão |
| GET | `/fotos-perfil/<arquivo>` | — (lê pelo armazenamento) | `200` imagem com o `Content-Type` do formato; `404` inexistente; `401` sem sessão |

Todas usam `exige_sessao` (CA30, D-004). O `usuario_id` vem sempre da sessão,
nunca da requisição (CA31). O nome do arquivo da foto é conferido contra o
padrão gerado (sem `/` nem `..`) antes de ler o disco.

## Front-end (`front/`) — PROJ-30, PROJ-27 e PROJ-29

Segue a arquitetura e o visual da spec 002 (D-030 a D-033): HTML, CSS e JS puros,
`tema.css`, sem `innerHTML`, textos em `mensagens.js`.

| Tela | Subtarefa | Conteúdo |
|---|---|---|
| `front/perfil/index.html` | PROJ-30 | Perfil comum (de `GET /auth/me`) somente leitura. Sem perfil de anunciante (`404`): botão "Completar perfil de anunciante". Com perfil: nome de exibição, foto, contatos (com o WhatsApp como link de conversa) e botão "Editar". |
| `front/perfil/anunciante/index.html` | PROJ-27 | Formulário: foto com pré-visualização e opção de remover; nome de exibição; **seção "Contatos"** com a lista de contatos, botão "Adicionar contato" (escolha do tipo: WhatsApp, e-mail, telefone, site ou link), remover e reordenar cada contato arrastando (alça; no teclado, setas); vínculo somente leitura. Cada tipo mostra seus campos: WhatsApp com escolha "Número" (lista de países, Brasil padrão) ou "Link"; telefone com lista de países; e-mail; site; link com rótulo opcional. Pré-preenchimento do CA4 ou do CA5. |
| `front/anuncios/novo/index.html` | PROJ-29 | Página provisória de novo anúncio: usa a guarda abaixo e mostra que a publicação ainda está em construção. |

Módulos JS:

- `js/dominio/codigos_paises.js`: lista de países e códigos, com o Brasil
  como padrão.
- `js/dominio/regras_perfil.js`: as mesmas regras do core para aviso imediato
  (obrigatórios, ao menos um contato, no máximo 10, repetidos, dígitos de
  número, host do link de WhatsApp, `https://` de site e link, formatos e 2 MB
  da foto). O backend continua sendo a validação definitiva.
- `js/fluxos/obter_perfil.js`: junta `GET /auth/me` e
  `GET /perfil-anunciante` no estado da tela de perfil e do formulário.
- `js/fluxos/salvar_perfil.js`: envia o `multipart` e devolve o estado para
  `200`, `400`, `413` e `401`; com `?depois=anunciar`, o destino após salvar
  é `/anuncios/novo/` (CA28).
- `js/fluxos/carregar_foto.js`: baixa a foto com o token e devolve um
  endereço `blob:` (revogado ao trocar de foto ou sair da tela).
- `js/fluxos/exigir_perfil_anunciante.js` (PROJ-29): com `404`, leva para
  `/perfil/anunciante/?depois=anunciar` (CA27); com `200`, segue (CA29).
- `/inicio/` ganha os links "Meu perfil" e "Anunciar".

## Princípios SOLID aplicados

- **S:** obter e salvar o perfil são casos de uso separados; validação do
  contato (`Contato`), da foto (`FotoDePerfil`) e gravação de arquivos
  (`ArmazenamentoDeFoto`) ficam em peças separadas.
- **O:** um novo tipo de contato é um novo valor de `TipoDeContato` com sua
  regra em `Contato`; trocar o disco local por um serviço de arquivos é só
  outra implementação de `ArmazenamentoDeFotoInterface`.
- **L:** o repositório e o armazenamento em memória dos testes cumprem as
  mesmas interfaces das implementações reais.
- **I:** o repositório de anunciante e o armazenamento de foto são interfaces
  pequenas e independentes.
- **D:** os casos de uso recebem repositório e armazenamento pelo construtor;
  a montagem fica em `server/app.py`.

## Estratégia de testes

- `tests/core/entities/`: `Contato` (WhatsApp por número com máscara e `+`;
  código do país obrigatório; 7 e 16 dígitos no total recusados, 8 e 15
  aceitos; código com 4 dígitos recusado; letras recusadas; WhatsApp por link
  `wa.me/<número>`, `wa.me/message/...` e `api.whatsapp.com/send?phone=`
  aceitos; `http://`, outros hosts, host falso, usuário no endereço, porta e
  `javascript:` recusados; telefone com e sem país; e-mail de qualquer domínio
  e inválido; site e link só com `https://`, sem espaços, sem usuário, com
  ponto no host; rótulo só em link; código do país onde não cabe;
  `link_de_conversa`); `Anunciante` (nome obrigatório, 0 / 1 / 10 / 11
  contatos, repetidos, aceita lista, mesmos contatos em tipos diferentes
  aceitos); `FotoDePerfil` (JPEG, PNG e WEBP pela assinatura; exatamente 2 MB
  aceita; 2 MB + 1 byte recusa; GIF, PDF e texto com nome `.jpg` recusados).
- `tests/core/usecases/`: `SalvarPerfilAnunciante` e `ObterPerfilAnunciante`
  com repositório e armazenamento em memória (em `fakes.py`), incluindo RN8
  (foto ou contato inválido não grava nada; falha ao salvar apaga a foto
  nova), qual contato falhou, ordem preservada, remoção de contato, e a
  troca/remoção da foto antiga.
- `tests/infra/`: constraints das tabelas `anunciantes` e
  `contatos_anunciante` (um perfil por usuário, restrições por tipo,
  posição única, cascade em duas etapas), gateway (ida e volta de todos os
  tipos, ordem, substituição da lista, outros usuários intactos) e
  armazenamento local (com `tmp_path`).
- `tests/api/`: rotas com e sem sessão, `multipart` com foto válida, grande e
  falsa, JSON de contatos malformado, `413`, fluxo `404` → `PUT` → `GET`, foto
  com e sem sessão e nome de arquivo com `..`.
- `front/`: `node --test` em `regras_perfil.js` e nos fluxos; telas pelo
  roteiro de teste manual.

### Mapa critério → teste

| CA | Onde é testado |
|---|---|
| CA1, CA10 | fluxo `obter_perfil.js` (dados de `/auth/me`) + roteiro manual |
| CA2, CA3 | fluxo `obter_perfil.js` (`404` e `200`) + API `GET` |
| CA4, CA5 | fluxo `obter_perfil.js` (pré-preenchimento e ordem) |
| CA6, CA9 | use case `SalvarPerfilAnunciante` (cria e atualiza) + API `PUT` |
| CA7, CA8 | entidade `Anunciante` + use case |
| CA11 | `Contato.criar` (tipo inválido) + roteiro manual do formulário |
| CA12, CA13, CA14, CA15 | `Contato` + use case + `regras_perfil.js` |
| CA16, CA17, CA18 | `Contato` + `regras_perfil.js` |
| CA19, CA20 | use case + gateway (ordem preservada, remoção) + roteiro manual |
| CA21, CA22 | entidade `Anunciante` + use case + `regras_perfil.js` |
| CA23, CA24 | `FotoDePerfil` + use case (nada gravado) + API (`400`, `413`) |
| CA25, CA26 | use case (sem foto, remover, manter a atual) |
| CA27, CA29 | fluxo `exigir_perfil_anunciante.js` + API `GET` `404`/`200` |
| CA28 | fluxo `salvar_perfil.js` (destino com `?depois=anunciar`; valor fora da lista ignorado) |
| CA30 | API sem sessão → `401` nas três rotas + fluxo do front leva a `/entrar/` |
| CA31 | API: a rota não recebe id; o perfil salvo é o do usuário da sessão |

## Impacto em código existente

- `server/core/usecases/erros.py`: novos erros.
- `server/api/erros_http.py`: mapear `PerfilNaoEncontrado` (`404`, código
  `perfil_nao_encontrado`), `FotoInvalida` (`400`, código `foto_invalida`) e
  `413`.
- `server/app.py`: montar os novos casos de uso, `MAX_CONTENT_LENGTH` e
  `FOTOS_PERFIL_DIR`.
- `tests/core/usecases/fakes.py`: repositório de anunciante e armazenamento
  de foto em memória.
- `front/inicio/index.html`: links "Meu perfil" e "Anunciar".
- `ARQUITETURA.md`: seção "Perfil de anunciante" atualizada para as decisões
  desta spec.
- `README.md` raiz: documentar `FOTOS_PERFIL_DIR`.
