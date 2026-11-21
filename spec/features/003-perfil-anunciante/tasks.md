# Tarefas: Perfil de anunciante

Referências: `spec.md` e `plan.md` desta pasta; `spec/decisoes.md`.
Jira: PROJ-4. Marque `[x]` ao concluir. Escreva os testes antes da
implementação. Rode `pytest` ao fim de cada bloco.

> Em 2026-11-20 os contatos foram revistos (de "WhatsApp + e-mail" para uma
> lista de contatos de vários tipos, D-013). O bloco 1 já tinha sido feito com
> o modelo antigo e foi refeito.

## 1. PROJ-25 — Modelagem do anunciante e dos contatos

### Domain (`server/core/entities/`)

- [x] T1: Criar `politicas_perfil.py` com as constantes de foto, dígitos de
  telefone, hosts do WhatsApp, limite de contatos, de rótulo e de endereço.
- [x] T2: Testes de `TipoDeContato` e `Contato`: WhatsApp por número (máscara
  e `+` ignorados; código obrigatório e com 1 a 3 dígitos; 8 e 15 dígitos no
  total aceitos, 7 e 16 recusados; letras recusadas); WhatsApp por link
  (`wa.me/<número>`, `wa.me/message/...` e `api.whatsapp.com/send?phone=`
  aceitos; `http://`, outros hosts, host falso, usuário no endereço, porta e
  `javascript:` recusados); telefone (código obrigatório, mesma regra de
  dígitos); e-mail de qualquer domínio, normalizado, e inválido recusado; site
  e link só `https://`, sem espaços, sem usuário, com ponto no host, até 2048
  caracteres; rótulo só em link, até 40 caracteres, vazio vira `None`; código
  do país recusado em e-mail, site e link; tipo inexistente recusado;
  `link_de_conversa`. Implementar. (CA11–CA18)
- [x] T3: Testes de `Anunciante`: nome obrigatório e não só espaços; 0
  contatos recusado, 1 e 10 aceitos, 11 recusado; contatos repetidos
  recusados, mesmo valor em tipos diferentes aceito; aceita lista e guarda
  tupla; normalização da foto; `com_foto`/`sem_foto`. Implementar
  `anunciante.py`. (CA7, CA8, CA19–CA22)

### Interface (`server/core/interfaces/`)

- [x] T4: Criar `AnuncianteRepositoryInterface` (`buscar_por_usuario_id`,
  `salvar`).
- [x] T5: Adicionar `AnuncianteRepositoryEmMemoria` em
  `tests/core/usecases/fakes.py`.

### Infra (`server/infra/`) — seguir a skill `manter-modelagem-dados`

- [x] T6: Testes de banco em `tests/infra/db/test_database.py`: tabelas
  `anunciantes` e `contatos_anunciante` criadas também num banco que já tem
  `usuarios`; `usuario_id` único e obrigatório; `CHECK` de nome e foto;
  contato com tipo inexistente, `codigo_pais` onde não cabe (e-mail, site,
  link) e ausente no telefone, número com letras, código com 4 dígitos, total
  de 8 e 15 aceitos e de 7 e 16 recusados, WhatsApp por link com hosts
  aceitos e recusados, e-mail sem `@`, site e link sem `https://` ou com
  espaços, rótulo fora de link, `posicao` negativa ou repetida no mesmo
  anunciante (repetida em outro anunciante aceita); cascade usuário →
  anunciante → contatos.
- [x] T7: Criar `AnuncianteModel` e `ContatoAnuncianteModel` em `models.py` e
  atualizar `schema.sql` até T6 passar.
- [x] T8: Atualizar `server/infra/db/README.md`: diagrama, tabelas de colunas,
  regras fora do banco (mínimo/máximo de contatos e repetidos) e o mapeamento
  de nomes da PROJ-25 (`id_usuario` → `usuario_id`, `nome` →
  `nome_exibicao`, `whatsapp` e `email_contato` → linhas de
  `contatos_anunciante`).
- [x] T9: Testes e implementação de `AnuncianteRepositorySQLAlchemy`: cria,
  atualiza pelo `usuario_id`; ida e volta de todos os tipos de contato; ordem
  preservada; atualização substitui a lista inteira; outros usuários
  intactos; busca inexistente devolve `None`; remover o usuário remove tudo.

## 2. PROJ-28 — Salvar o perfil com foto

- [x] T10: Testes de `FotoDePerfil.de_bytes`: JPEG, PNG e WEBP pela
  assinatura; exatamente 2 MB aceita; 2 MB + 1 byte recusa; vazio, GIF, PDF e
  texto recusados. Implementar `FotoDePerfil` e `FormatoDeFoto`. (CA23, CA24)
- [x] T11: Criar `ArmazenamentoDeFotoInterface` e o dublê em memória em
  `fakes.py`. Adicionar `PerfilNaoEncontrado` e `FotoInvalida` em `erros.py`.
- [x] T12: Testes de `ObterPerfilAnunciante` (existe; não existe gera
  `PerfilNaoEncontrado`). Implementar. (CA2, CA3, CA27)
- [x] T13: Testes de `SalvarPerfilAnunciante`: cria (CA6); atualiza e
  substitui os contatos (CA9); dados inválidos (CA7, CA8); contato inválido
  indicando qual falhou (CA12–CA17); mais de 10 e repetidos (CA21, CA22);
  ordem preservada e remoção de contato (CA19, CA20); sem foto (CA25); com
  foto válida (CA23); foto inválida não grava nada (CA24, RN8); contato
  inválido não grava foto nem perfil (RN8); mantém a foto atual, remove a foto
  e apaga o arquivo (CA26); troca a foto e apaga a antiga; falha ao salvar
  apaga a foto nova. Implementar.
- [x] T14: Testes e implementação de `ArmazenamentoDeFotoLocal` com
  `tmp_path` (grava com nome aleatório e extensão do formato, devolve
  `/fotos-perfil/<arquivo>`, lê, remove; remover arquivo inexistente não
  falha; nome com `..` ou `/` é recusado). Adicionar `server/uploads/` ao
  `.gitignore`.
- [x] T15: Presenter `anunciante_presenter.py` (contatos com
  `link_de_conversa` nos WhatsApp) e mapeamento dos novos erros e do `413` em
  `erros_http.py`.
- [x] T16: Testes de API em `tests/api/test_perfil_anunciante_controller.py`:
  `GET` `404` → `PUT` `200` → `GET` `200` com contatos na ordem; `PUT` com
  foto válida, grande (`400`), falsa (`400`), acima de 3 MB (`413`) e com JSON
  de contatos malformado (`400`); foto com sessão (`200` e `Content-Type`) e
  sem sessão (`401`); as três rotas sem sessão dão `401` (CA30); o perfil
  salvo é o do usuário da sessão (CA31).
- [x] T17: Implementar `perfil_anunciante_controller.py` e montar tudo em
  `server/app.py` (`FOTOS_PERFIL_DIR`, `MAX_CONTENT_LENGTH`) até T16 passar.

## 3. PROJ-30 e PROJ-27 — Tela de perfil e formulário

- [x] T18: Criar `front/js/dominio/codigos_paises.js` (Brasil como padrão) e
  testes (`node --test`) e implementação de `regras_perfil.js` (obrigatórios,
  ao menos um e no máximo 10 contatos, repetidos, dígitos de número, host do
  WhatsApp por link, `https://` de site e link, rótulo, formatos e tamanho da
  foto). Textos novos em `mensagens.js`.
- [x] T19: Testes e implementação de `obter_perfil.js` (perfil comum de
  `/auth/me`; com e sem perfil de anunciante; pré-preenchimento com nome e
  contato de e-mail institucional, CA4; dados e ordem atuais, CA5; `401` leva
  a `/entrar/`) e `carregar_foto.js` (com token; `blob:` revogado).
- [x] T20: Criar `front/perfil/index.html` (PROJ-30): perfil comum somente
  leitura e seção de anunciante com "Completar perfil de anunciante" ou dados,
  contatos + "Editar". (CA1–CA3)
- [x] T21: Testes e implementação de `salvar_perfil.js` (monta o `multipart`
  com os contatos em JSON; estados para `200`, `400`, `413` e `401`; destino
  após salvar com `?depois=anunciar` e valor fora da lista ignorado, CA28).
- [x] T22: Criar `front/perfil/anunciante/index.html` (PROJ-27): foto com
  pré-visualização e remoção, nome de exibição, seção "Contatos" (adicionar
  por tipo, remover, reordenar arrastando, com setas no teclado; campos de cada tipo) e
  vínculo somente leitura (CA10), no tema da spec 002 (RN11).

## 4. PROJ-29 — Exigir perfil de anunciante antes de anunciar

- [ ] T23: Testes e implementação de `exigir_perfil_anunciante.js` (com
  perfil segue, CA29; com `404` leva a `/perfil/anunciante/?depois=anunciar`,
  CA27).
- [ ] T24: Criar `front/anuncios/novo/index.html` provisória usando a guarda
  de T23, e os links "Meu perfil" e "Anunciar" em `/inicio/`.

## 5. Documentação

- [ ] T25: Documentar `FOTOS_PERFIL_DIR` e a pasta `server/uploads/` no
  `README.md` raiz.
- [ ] T26: Atualizar a seção "Perfil de anunciante" do `ARQUITETURA.md` e a
  lista de rotas públicas/protegidas.

## 6. Validação

- [ ] T27: `pytest` passando.
- [ ] T28: `flake8` sem erros.
- [ ] T29: `node --test` passando em `front/`.
- [ ] T30: Roteiro manual das telas (CA1–CA5, CA10, CA11, CA19, CA20,
  CA27–CA29, RN11 e upload de uma foto real de celular).
- [ ] T31: Conferir o mapa critério → teste do `plan.md`: CA1–CA31 com teste
  passando. Marcar os critérios na `spec.md` e mudar o status para
  `Implementada`.
