# Spec: Visualizar feed de anúncios

- **ID**: 001
- **Jira**: PROJ-7
- **Status**: Aprovada
- **Data**: 2026-11-12

## História de usuário

**Como** membro da comunidade universitária,
**quero** visualizar os anúncios publicados,
**para que** eu possa encontrar produtos/serviços do meu interesse.

- A história depende do contrato de publicação de anúncios definido pela PROJ-15.
- O feed assume que os anúncios publicados respeitam as validações de produto e serviço.

## Critérios de aceitação

- [ ] CA1: Dado que existam anúncios publicados e o usuário esteja autenticado, quando ele acessar o feed, então os anúncios serão exibidos em cards.

- [ ] CA2: Dado que um anúncio possua foto, quando ele for exibido no feed, então o card mostrará a foto, o título, a categoria, o preço e a data de criação.

- [ ] CA3: Dado que um anúncio não possua foto, quando ele for exibido no feed, então o card manterá sua estrutura sem quebrar o layout.

- [ ] CA4: Dado que existam mais de 20 anúncios publicados, quando o usuário acessar uma página numerada do feed, então serão exibidos no máximo 20 anúncios.

- [ ] CA5: Dado que existam anúncios em mais de uma página, quando o usuário solicitar outra página numerada, então serão exibidos os anúncios correspondentes à página solicitada.

- [ ] CA6: Dado que existam dois ou mais anúncios publicados, quando o feed for exibido, então os anúncios aparecerão do mais recente para o mais antigo.

- [ ] CA7: Dado que existam anúncios não publicados, vendidos ou expirados, quando o usuário acessar o feed, então esses anúncios não serão exibidos.

- [ ] CA8: Dado que não existam anúncios publicados disponíveis, quando o usuário acessar o feed, então o sistema retornará uma lista vazia e exibirá uma mensagem informativa.

- [ ] CA9: Dado que o usuário esteja autenticado e visualize um card, quando ele clicar no card, então será direcionado para a página de detalhes do anúncio.

- [ ] CA10: Dado que o usuário não esteja autenticado, quando tentar acessar o feed, então o sistema aplicará o comportamento de autenticação definido pela aplicação.

- [ ] CA11: Dado que existam anúncios correspondentes a um termo, quando o usuário realizar uma busca, então serão exibidos os anúncios cujo título, descrição ou categoria contenha o termo informado.

- [ ] CA12: Dado que o usuário selecione Todos, Produtos ou Serviços, quando o filtro for aplicado, então serão exibidos somente os anúncios do tipo selecionado, exceto quando Todos estiver selecionado.

- [ ] CA13: Dado que o usuário informe uma busca ou selecione um filtro de tipo, quando a busca ou filtro for aplicado, então a listagem retornará à primeira página.

- [ ] CA14: Dado que um anúncio do tipo serviço possua descrição, quando ele for exibido no feed, então o card mostrará uma versão resumida da descrição.

## Regras de negócio

- RN1: Apenas anúncios publicados aparecem no feed.
- RN2: Os anúncios são ordenados pela data de criação, do mais recente para o mais antigo.
- RN3: O feed contém 20 anúncios por página.
- RN4: A primeira página é usada quando nenhuma página é informada.
- RN5: Anúncios vendidos não aparecem no feed.
- RN6: Anúncios não renovados expiram após 30 dias e não aparecem no feed.
- RN7: A paginação do feed é numerada.
- RN8: O clique em um card direciona para a página de detalhes do anúncio, conforme a PROJ-17.
- RN9: A busca considera título, descrição e categoria, sem diferenciar maiúsculas e minúsculas.
- RN10: Os filtros Todos, Produtos e Serviços podem ser usados junto com a busca.
- RN11: Aplicar ou alterar uma busca ou filtro inicia a listagem na primeira página.
- RN12: Cards de serviços podem exibir uma descrição resumida além dos campos comuns.

## Fora do escopo

- Criar novos anúncios.
- Editar anúncios.
- Excluir anúncios.
- Filtrar anúncios por categoria, preço ou usuário.
- Ordenar anúncios por qualquer critério diferente da data de criação.
- Implementar a página de detalhes do anúncio.

## Dúvidas em aberto

- Nenhuma.
