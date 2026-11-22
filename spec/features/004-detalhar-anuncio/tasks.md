# Tarefas: Detalhar anúncio

Referências: `spec.md`, `plan.md` e `wireframe.md`.
Jira: PROJ-17. Marque `[x]` ao concluir. Escreva os testes antes da
implementação. Rode `pytest` e `flake8` ao fim de cada bloco.

## 0. Decisões pendentes

- [x] T1: Confirmar localização no campus, estado de conservação, fallback sem
  foto e comportamento geral de anúncio vendido/expirado. Decidido: sem
  localização nesta feature; reutilizar `estado_conservacao`; ocultar a galeria
  sem foto; manter mensagens distintas para estados indisponíveis.
- [x] T2: Confirmar o contrato de fotos e manter uma foto opcional por anúncio.
  Não ampliar a publicação com múltiplas fotos nesta feature.
- [x] T3: Confirmar o wireframe textual descrito em PROJ-17:
  carrossel/galeria à esquerda, informações do item à direita e bloco do
  anunciante com contatos à direita. Os textos exatos das mensagens foram
  definidos na seção "Mensagens da página" da spec.

## 1. PROJ-48 — Back-end

### Domain (`server/core/entities/`)

- [x] T4: Escrever testes da representação de detalhes, foto opcional,
  anúncio indisponível e resumo público do anunciante.
- [x] T5: Implementar as entidades necessárias em
  `server/core/entities/` sem depender de HTTP ou banco.

### Use cases (`server/core/usecases/`)

- [x] T6: Definir a interface necessária para consultar anúncio por id e dados
  do anunciante em `server/core/interfaces/`.
- [x] T7: Escrever testes de `ObterDetalhesAnuncio` com repositórios em memória:
  sucesso autenticado, id inexistente, excluído, vendido, expirado,
  não publicado e usuário sem sessão.
- [x] T8: Implementar `ObterDetalhesAnuncio` e os erros específicos do domínio.

### Infra (`server/infra/`)

- [x] T9: Fechar a modelagem persistente das fotos e dos campos pendentes.
  Atualizar entidade, modelo SQLAlchemy, `schema.sql` e README da base juntos,
  conforme `manter-modelagem-dados`. Não houve mudança persistida adicional:
  anúncio já possui uma foto opcional e anunciante já usa tabelas existentes.
- [x] T10: Escrever testes do repositório para buscar por id, excluir estados
  indisponíveis, carregar a foto opcional e anunciante/contatos.
- [x] T11: Implementar a consulta SQLAlchemy sem vazamento de dados privados.

### Web (`server/api/`)

- [x] T12: Escrever testes da rota `GET /api/ads/<id>` para `200`, `400`,
  `401`, `404`, indisponibilidade e falha de persistência.
- [x] T13: Implementar controller, presenter e montagem das dependências em
  `server/app.py`.

## 2. PROJ-49 — Front-end

- [x] T14: Escrever testes dos módulos da página para dados completos,
  foto, fallback sem foto e links de contato.
- [x] T15: Criar `front/anuncios/detalhes/index.html` seguindo o wireframe e o
  guia de estilo.
- [x] T16: Implementar o carregamento autenticado de anúncio e anunciante,
  exibindo título, categoria, conservação, preço e descrição.
- [x] T17: Implementar a foto com rótulo acessível e estado sem foto.
- [x] T18: Implementar o bloco do anunciante com foto, vínculo e contatos
  reutilizando as regras e formatos de D-013.
- [x] T19: Implementar estados de carregamento, falha de conexão, não encontrado
  e indisponível.
- [x] T20: Garantir responsividade, rótulos acessíveis e ausência de
  `innerHTML`.

## 3. Integração e validação

- [x] T21: Conectar o clique do card do feed à rota da página detalhada.
- [ ] T22: Executar `pytest` completo e confirmar cobertura dos critérios de aceitação.
- [x] T23: Executar `flake8` nos arquivos alterados.
- [x] T24: Executar `node --test` e validar os módulos do front.
  Resultado: 119 testes, todos aprovados.
- [x] T25: Roteiro manual em celular e teclado dispensado para esta entrega
  acadêmica pelo solicitante. Continua coberto como critério de aceitação
  da feature, mas não será executado como validação física nesta etapa.
- [x] T26: Conferir a conformidade com `wireframe.md`, o tema e o guia de estilo.
- [x] T27: Spec aprovada explicitamente pelo time e mantida em `Aprovada`.

