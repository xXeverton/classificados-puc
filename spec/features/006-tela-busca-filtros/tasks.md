# Tarefas: Tela de busca e filtros do feed

Referências: `spec.md` e `plan.md` desta pasta. Jira: PROJ-46 e PROJ-47.
Marque `[x]` ao concluir. Escreva os testes antes da implementação.

## Domínio do front

- [x] T1: Testes em `front/tests/feed.test.js` para preço na URL, faixa de
  preço, contador, limpar e mensagem de feed vazio.
- [x] T2: Implementar as funções em `front/js/dominio/feed.js`.

## Back-end

- [x] T3: Teste do repositório: "a combinar" fica fora com filtro de preço.
- [x] T4: Excluir `preco_a_combinar` quando há filtro de preço.

## Tela (PROJ-46)

- [x] T5: Botão "Filtros", menu retrátil e "Limpar filtros e busca" em
  `front/inicio/index.html` e `front/css/tema.css`.

## Estado e requisições (PROJ-47)

- [x] T6: `front/js/paginas/inicio.js` usa o domínio para URL, requisição,
  contador, erros e feed vazio.

## Validação

- [x] T7: `pytest` e `flake8` passando.
- [ ] T8: `node --test` no front (precisa de Node 18 ou mais novo). Não rodou: a máquina de desenvolvimento não tem Node; os mesmos casos foram executados no navegador.
- [x] T9: Teste no navegador conferindo CA1–CA8.
