# Spec: Painel "Meus Anúncios"

- **ID**: 009
- **Status**: Rascunho
- **Data**: 2026-11-22
- **Jira**: história [PROJ-15](https://matheuscomputacaopuc.atlassian.net/browse/PROJ-15)
  (Gerenciar anúncios); subtarefa
  [PROJ-37](https://matheuscomputacaopuc.atlassian.net/browse/PROJ-37)
  ("Meus Anúncios")
- **Decisões gerais aplicadas**: D-004, D-020, D-021, D-030, D-032, D-033, D-034
- **Relacionadas**: [007-editar-excluir-anuncio](../007-editar-excluir-anuncio/spec.md)
  e [004-expirar-anuncios](../004-expirar-anuncios/spec.md)

## História de usuário

**Como** anunciante,
**quero** visualizar em um painel os anúncios cadastrados por mim,
**para que** eu possa consultar meus itens e identificá-los para gerenciá-los.

## Critérios de aceitação

- [ ] CA1: Dado um usuário autenticado com anúncios próprios, quando ele abre
  o painel, então são exibidos somente os anúncios cujo dono é esse usuário.
- [ ] CA2: Dado um anúncio próprio com foto, quando ele aparece no painel,
  então o card mostra foto, título, categoria, preço ou "A combinar", estado
  quando aplicável e data.
- [ ] CA3: Dado um anúncio próprio sem foto, quando ele aparece no painel,
  então o card mantém o layout sem quebrar a página.
- [ ] CA4: Dado um usuário autenticado sem anúncios próprios, quando ele abre
  o painel, então o sistema mostra uma mensagem informativa de lista vazia.
- [ ] CA5: Dado um usuário não autenticado, quando ele tenta abrir o painel,
  então ele é direcionado ao comportamento de sessão definido pela aplicação.
- [ ] CA6: Dado que a API de anúncios do usuário falhe, quando o painel tenta
  carregar, então o usuário recebe um aviso de erro sem dados fictícios.
- [ ] CA7: Dado um anúncio próprio publicado, quando ele aparece no painel,
  então o card oferece ações de editar, excluir e renovar.
- [ ] CA8: Dado mais anúncios do que cabem em uma página, quando o usuário
  navega pelas páginas, então o painel mostra a página correspondente.

## Regras de negócio

- RN1: O painel mostra somente anúncios pertencentes ao usuário da sessão.
- RN2: A autenticação é obrigatória para acessar o painel.
- RN3: O front não apresenta dados globais ou de outros usuários como se fossem
  do usuário atual.
- RN4: A aparência segue o tema e o guia de estilo existentes.
- RN5: A consulta usa `GET /api/ads?owner=me` e passa o usuário da sessão.
- RN6: Somente anúncios com estado `published` disponíveis são listados.
- RN7: Os resultados são ordenados pela data de criação, do mais recente para o
  mais antigo.
- RN8: A listagem usa 20 itens por página e suporta o parâmetro `page`.
- RN9: Os cards oferecem Editar, Excluir e Renovar.

## Fora do escopo

- Implementar novos contratos de edição ou exclusão nesta feature; os
  contratos existentes estão definidos pela PROJ-38 e pela spec 007.
- Confirmar ou criar o contrato da renovação nesta feature; ela é parte da
  interface do painel, mas depende da tarefa PROJ-40.
- Mostrar anúncios vendidos ou expirados no painel.
- Criar anúncios nesta feature.
- Implementar filtros, busca ou seleção em massa não confirmados no Jira.
- Exibir dados de perfil do anunciante para compradores.

## Dúvidas em aberto

- Qual contrato HTTP da renovação será usado pela PROJ-40?
- Como a renovação se comporta para um anúncio publicado antes da expiração?
