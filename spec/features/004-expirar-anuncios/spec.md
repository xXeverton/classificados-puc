# Spec: Expirar anúncios não renovados

- **ID**: 004
- **Status**: Rascunho
- **Data**: 2026-11-21
- **Jira**: história [PROJ-15](https://matheuscomputacaopuc.atlassian.net/browse/PROJ-15)
  (Gerenciar anúncios); subtarefa
  [PROJ-39](https://matheuscomputacaopuc.atlassian.net/browse/PROJ-39)
  (rotina que marca anúncios como expirados)
- **Decisões gerais aplicadas**: nenhuma

## História de usuário

**Como** membro da comunidade que navega pelo feed,
**quero** que anúncios não renovados há mais de 30 dias saiam do feed sozinhos,
**para que** eu só veja ofertas que provavelmente ainda estão disponíveis.

Esta spec cobre só a expiração automática da PROJ-15. Editar, excluir e
renovar ficam para as próximas subtarefas.

## Critérios de aceitação

- [ ] CA1: Dado um anúncio publicado cujo prazo de 30 dias já terminou, quando
  a rotina de expiração roda, então o anúncio passa a ficar expirado e deixa de
  aparecer no feed.
- [ ] CA2: Dado um anúncio publicado ainda dentro do prazo, quando a rotina
  roda, então ele continua publicado.
- [ ] CA3: Dado um anúncio renovado (com novo fim de prazo), quando a rotina
  roda, então vale o novo prazo, e não a data de publicação.
- [ ] CA4: Dado um anúncio vendido ou já expirado, quando a rotina roda, então
  a situação dele não muda.
- [ ] CA5: Dado que a rotina roda mais de uma vez, quando não há anúncios
  vencidos novos, então nada muda e ela informa que nenhum anúncio expirou.
- [ ] CA6: Quando a rotina termina, então ela informa quantos anúncios
  expirou.

## Regras de negócio

- RN1: Um anúncio publicado vale por 30 dias.
- RN2: O prazo termina na data de fim registrada no anúncio. Essa data é o que
  a renovação (PROJ-40) vai estender.
- RN3: Anúncio sem data de fim registrada vence 30 dias depois de publicado.
  Hoje nenhum anúncio tem essa data preenchida, porque a publicação (PROJ-2)
  ainda não existe.
- RN4: O anúncio expira no exato instante em que o prazo termina.
- RN5: Só anúncios publicados expiram. Vendidos e expirados não mudam.
- RN6: Expirar não apaga o anúncio. Apagar expirados há 30 dias é a PROJ-41.

## Fora do escopo

- Renovar anúncio (PROJ-40) e o painel "Meus Anúncios" (PROJ-37).
- Apagar anúncios expirados (PROJ-41).
- Avisar o anunciante antes de o anúncio expirar.
- Agendar a rotina no servidor de produção. O projeto ainda não tem um; a
  rotina fica pronta para ser chamada por um agendador (cron, Agendador de
  Tarefas do Windows).

## Dúvidas em aberto

- O PO precisa confirmar que os 30 dias contam da publicação ou da última
  renovação (RN2 e RN3). A PROJ-15 lista essa regra no Definition of Ready.
- Quando a publicação (PROJ-2) existir, ela deve gravar a data de fim
  (publicação + 30 dias). Combinar com quem implementar a PROJ-2.
- A subtarefa PROJ-39 fala em anúncios "sem atualização" há mais de 30 dias.
  Esta spec usa o prazo de publicação/renovação da PROJ-15, porque o anúncio
  não guarda data de última edição. Confirmar se editar também deve renovar
  o prazo.
