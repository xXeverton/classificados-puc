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

- [ ] T4: Escrever testes da representação de detalhes, fotos ordenadas,
  anúncio indisponível e resumo público do anunciante.
- [ ] T5: Implementar as entidades necessárias em
  `server/core/entities/` sem depender de HTTP ou banco.

### Use cases (`server/core/usecases/`)

- [ ] T6: Definir a interface necessária para consultar anúncio por id e dados
  do anunciante em `server/core/interfaces/`.
- [ ] T7: Escrever testes de `ObterDetalhesAnuncio` com repositórios em memória:
  sucesso autenticado, id inexistente, excluído, vendido, expirado,
  não publicado e usuário sem sessão.
- [ ] T8: Implementar `ObterDetalhesAnuncio` e os erros específicos do domínio.

### Infra (`server/infra/`)

- [ ] T9: Fechar a modelagem persistente das fotos e dos campos pendentes.
  Atualizar entidade, modelo SQLAlchemy, `schema.sql` e README da base juntos,
  conforme `manter-modelagem-dados`.
- [ ] T10: Escrever testes do repositório para buscar por id, excluir estados
  indisponíveis, preservar a ordem das fotos e carregar anunciante/contatos.
- [ ] T11: Implementar a consulta SQLAlchemy sem vazamento de dados privados.

### Web (`server/api/`)

- [ ] T12: Escrever testes da rota `GET /api/ads/<id>` para `200`, `400`,
  `401`, `404`, indisponibilidade e falha de persistência.
- [ ] T13: Implementar controller, presenter e montagem das dependências em
  `server/app.py`.

## 2. PROJ-49 — Front-end

- [ ] T14: Escrever testes dos módulos da página para dados completos,
  foto, fallback sem foto e links de contato.
- [ ] T15: Criar `front/anuncios/detalhes/index.html` seguindo o wireframe e o
  guia de estilo.
- [ ] T16: Implementar o carregamento autenticado de anúncio e anunciante,
  exibindo título, categoria, conservação, preço e descrição.
- [ ] T17: Implementar a foto com rótulo acessível e estado sem foto.
- [ ] T18: Implementar o bloco do anunciante com foto, vínculo e contatos
  reutilizando as regras e formatos de D-013.
- [ ] T19: Implementar estados de carregamento, falha de conexão, não encontrado
  e indisponível.
- [ ] T20: Garantir responsividade, rótulos acessíveis e ausência de
  `innerHTML`.

## 3. Integração e validação

- [ ] T21: Conectar o clique do card do feed à rota da página detalhada.
- [ ] T22: Executar `pytest` e confirmar cobertura dos critérios de aceitação.
- [ ] T23: Executar `flake8` sem erros.
- [ ] T24: Executar `node --test` e validar os módulos do front.
- [ ] T25: Fazer roteiro manual em celular e teclado.
- [ ] T26: Conferir a conformidade com `wireframe.md`, o tema e o guia de estilo.
- [ ] T27: Marcar os critérios conferidos na `spec.md` e alterar o status para
  `Aprovada` só após confirmação explícita do time.

