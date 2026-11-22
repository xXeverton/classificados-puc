# Spec: Marcar anúncio como vendido (back-end)

- **ID**: 011
- **Status**: Rascunho
- **Data**: 2026-11-22
- **Jira**: história [PROJ-14](https://matheuscomputacaopuc.atlassian.net/browse/PROJ-14)
  (Alterar status do produto para "Vendido"); subtarefa
  [PROJ-35](https://matheuscomputacaopuc.atlassian.net/browse/PROJ-35)
  (`PATCH /api/ads/:id/status`)
- **Decisões gerais aplicadas**: nenhuma
- **Relacionadas**: [007-editar-excluir-anuncio](../007-editar-excluir-anuncio/spec.md),
  [009-painel-meus-anuncios](../009-painel-meus-anuncios/spec.md) e
  [010-expirar-anuncios](../010-expirar-anuncios/spec.md)

## História de usuário

**Como** anunciante,
**quero** marcar meu anúncio como vendido (e desfazer, se precisar),
**para que** os compradores saibam que o item não está mais disponível.

Esta spec cobre o back-end da PROJ-35. O botão "Marcar como vendido" é a
PROJ-36.

## Critérios de aceitação

- [ ] CA1: Dado um anúncio meu publicado, quando o marco como vendido, então
  ele passa a ficar vendido e sai do feed e da busca.
- [ ] CA2: Dado um anúncio meu expirado, quando o marco como vendido, então
  ele também passa a ficar vendido.
- [ ] CA3: Dado um anúncio meu vendido, quando o reativo, então ele volta a
  ficar publicado se ainda estiver no prazo; se o prazo já acabou, volta como
  expirado, e posso renová-lo.
- [ ] CA4: Dado um anúncio de outra pessoa (ou sem dono), quando tento mudar o
  status, então a ação é recusada e nada muda.
- [ ] CA5: Dado um status desconhecido ou uma mudança que não faz sentido
  (reativar um anúncio que não está vendido), quando envio, então recebo um
  erro explicando o motivo.
- [ ] CA6: Dado que sou o dono, quando listo meus anúncios vendidos no painel,
  então eles aparecem; ninguém mais consegue listá-los.

## Regras de negócio

- RN1: Só o dono muda o status (mesma regra da spec 007).
- RN2: A ação vale para produtos, serviços e eventos.
- RN3: Vender é permitido para anúncios publicados ou expirados. Marcar como
  vendido um anúncio já vendido não muda nada e não é erro.
- RN4: Reativar só vale para anúncios vendidos. O prazo de publicação não
  muda: no prazo, volta como publicado; fora dele, volta como expirado
  (decisão desta spec, a confirmar com o PO).
- RN5: Anúncios vendidos não aparecem no feed nem na busca (já era assim) e
  continuam no banco; eles não entram na limpeza da spec 008.
- RN6: A listagem de vendidos (`status=sold`) só é permitida com
  `owner=me`.

## Fora do escopo

- O botão na tela e a confirmação antes de marcar (PROJ-36).
- Selo "Vendido" na página de detalhes.
- Avisar quem conversou com o anunciante.

## Dúvidas em aberto

- O PO precisa confirmar que a ação é reversível (RN4) e que vale para
  serviços e eventos (RN2).
