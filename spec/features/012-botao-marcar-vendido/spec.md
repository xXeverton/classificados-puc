# Spec: Botão "Marcar como vendido" no painel

- **ID**: 012
- **Status**: Rascunho
- **Data**: 2026-11-22
- **Jira**: história [PROJ-14](https://matheuscomputacaopuc.atlassian.net/browse/PROJ-14);
  subtarefa [PROJ-36](https://matheuscomputacaopuc.atlassian.net/browse/PROJ-36)
- **Decisões gerais aplicadas**: nenhuma
- **Relacionadas**: [011-marcar-anuncio-vendido](../011-marcar-anuncio-vendido/spec.md)
  (API) e [009-painel-meus-anuncios](../009-painel-meus-anuncios/spec.md)

## História de usuário

**Como** anunciante,
**quero** marcar meus anúncios como vendidos pelo painel "Meus anúncios" (e
reativá-los se precisar),
**para que** os compradores parem de ver itens que já vendi.

## Critérios de aceitação

- [ ] CA1: Dado um anúncio meu publicado ou expirado no painel, quando clico em
  "Marcar como vendido" e confirmo, então ele sai da lista em que estava e
  aparece na lista "Vendidos", com uma mensagem de sucesso.
- [ ] CA2: Dado que cancelo a confirmação, então nada muda.
- [ ] CA3: Dado um anúncio meu vendido, quando clico em "Reativar" e confirmo,
  então ele volta para "Publicados" (ou "Expirados", se o prazo já acabou).
- [ ] CA4: Dado que a ação falha, então vejo a mensagem de erro da API e as
  listas não mudam.
- [ ] CA5: Dado que tenho anúncios vendidos, quando abro o painel, então vejo a
  seção "Vendidos" com eles; sem vendidos, vejo uma mensagem de lista vazia.

## Regras de negócio

- RN1: Ações por situação do anúncio:
  - publicado: Editar, Marcar como vendido, Excluir;
  - expirado: Editar, Marcar como vendido, Renovar, Excluir;
  - vendido: Reativar, Excluir.
- RN2: Marcar como vendido e reativar pedem confirmação antes de chamar a API.

## Fora do escopo

- Botão na página de detalhes: a API de detalhes não informa se quem está
  vendo é o dono. Fica para quando essa informação existir.

## Dúvidas em aberto

- O PO precisa aprovar o texto dos botões e das confirmações.
