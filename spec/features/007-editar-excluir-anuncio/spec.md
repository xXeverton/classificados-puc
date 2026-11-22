# Spec: Editar e excluir anúncio

- **ID**: 007
- **Status**: Rascunho
- **Data**: 2026-11-22
- **Jira**: história [PROJ-15](https://matheuscomputacaopuc.atlassian.net/browse/PROJ-15)
  (Gerenciar anúncios); subtarefa
  [PROJ-38](https://matheuscomputacaopuc.atlassian.net/browse/PROJ-38)
  (`PUT` e `DELETE /api/ads/:id`)
- **Decisões gerais aplicadas**: nenhuma
- **Relacionadas**: publicação de anúncios (PROJ-2) e
  [004-expirar-anuncios](../004-expirar-anuncios/spec.md)

## História de usuário

**Como** anunciante,
**quero** editar ou excluir meus anúncios,
**para que** eu possa atualizar informações ou remover itens que não estou
mais oferecendo.

Esta spec cobre só o back-end da PROJ-38. O painel "Meus Anúncios" é a
PROJ-37 e a renovação é a PROJ-40.

## Critérios de aceitação

- [ ] CA1: Dado um anúncio meu, quando altero o preço e salvo, então o novo
  valor passa a aparecer no feed.
- [ ] CA2: Dado um anúncio meu, quando altero título, descrição, estado de
  conservação ou troco para "a combinar", então as mudanças são salvas com as
  mesmas regras da publicação.
- [ ] CA3: Dado dados inválidos na edição, quando salvo, então vejo os erros
  por campo e o anúncio não muda.
- [ ] CA4: Dado um anúncio meu, quando confirmo a exclusão, então ele é
  removido do banco e do feed, e a foto dele é apagada.
- [ ] CA5: Dado um anúncio de outra pessoa, quando tento editar ou excluir,
  então a ação é recusada e o anúncio não muda.
- [ ] CA6: Dado um anúncio que não existe, quando tento editar ou excluir,
  então recebo a resposta de anúncio não encontrado.

## Regras de negócio

- RN1: Só o dono do anúncio pode editar ou excluir. Anúncios antigos, sem
  dono registrado, não podem ser editados nem excluídos pela API.
- RN2: A edição envia o anúncio completo, com os mesmos campos e validações da
  publicação (título, descrição, categoria, estado de conservação, preço ou
  "a combinar").
- RN3: A categoria (produto, serviço ou evento) não pode ser trocada, porque
  ela define o tipo do anúncio e quais campos valem.
- RN4: Editar não muda a data de publicação nem o prazo de expiração;
  estender o prazo é a renovação (PROJ-40).
- RN5: A exclusão é definitiva: o anúncio sai do banco e a foto é apagada do
  armazenamento.

## Fora do escopo

- Trocar ou remover a foto na edição: fica para um segundo passo, porque
  envolve o armazenamento de imagens.
- Confirmação de exclusão na tela e painel "Meus Anúncios" (PROJ-37).
- Renovar o prazo (PROJ-40).

## Dúvidas em aberto

- O PO precisa confirmar se título e categoria podem ser editados. Esta spec
  permite título e bloqueia categoria (RN3).
- Confirmar se anúncios vendidos ou expirados podem ser editados. Esta spec
  permite editar em qualquer situação.
