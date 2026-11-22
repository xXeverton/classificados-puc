# Spec: Apagar anúncios expirados há mais de 30 dias

- **ID**: 008
- **Status**: Rascunho
- **Data**: 2026-11-22
- **Jira**: história [PROJ-15](https://matheuscomputacaopuc.atlassian.net/browse/PROJ-15)
  (Gerenciar anúncios); subtarefa
  [PROJ-41](https://matheuscomputacaopuc.atlassian.net/browse/PROJ-41)
  (excluir anúncios expirados 30 dias atrás)
- **Decisões gerais aplicadas**: nenhuma
- **Relacionada**: [004-expirar-anuncios](../004-expirar-anuncios/spec.md),
  que marca os anúncios como expirados.

## História de usuário

**Como** responsável pela plataforma,
**quero** que anúncios expirados e não renovados sejam apagados depois de um
tempo,
**para que** o banco e o armazenamento de fotos não acumulem anúncios
abandonados.

## Critérios de aceitação

- [ ] CA1: Dado um anúncio expirado cujo prazo terminou há 30 dias ou mais,
  quando a rotina roda, então ele é apagado do banco e a foto dele é apagada.
- [ ] CA2: Dado um anúncio expirado há menos de 30 dias, quando a rotina roda,
  então ele continua no banco, podendo ainda ser renovado.
- [ ] CA3: Dado um anúncio publicado ou vendido, quando a rotina roda, então
  ele não é apagado, qualquer que seja a data.
- [ ] CA4: Dado que a rotina roda de novo sem anúncios novos para apagar,
  então nada muda.
- [ ] CA5: Quando a rotina termina, então ela informa quantos anúncios apagou.

## Regras de negócio

- RN1: Só anúncios com situação "expirado" são apagados.
- RN2: Um anúncio expirado é apagado 30 dias depois do fim do prazo de
  publicação (o mesmo prazo da spec 004: `expires_at` ou, sem ele, a data de
  publicação mais 30 dias). Sem renovação, isso dá 60 dias depois de
  publicado.
- RN3: Apagar é definitivo: o anúncio sai do banco e a foto sai do
  armazenamento.
- RN4: Se a foto não puder ser apagada, a falha é registrada no log e o
  anúncio continua apagado.

## Fora do escopo

- Avisar o anunciante antes de apagar.
- Agendar a rotina no servidor de produção (mesma situação da spec 004).

## Dúvidas em aberto

- O PO precisa confirmar que os 30 dias contam do fim do prazo, e não da data
  em que a rotina de expiração marcou o anúncio (RN2).
