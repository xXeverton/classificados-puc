# Plano técnico: Botão "Marcar como vendido" no painel

Referência: `spec.md` desta pasta.

## Front

- `front/js/dominio/meus_anuncios.js` (novo, sem DOM): `SECOES_DO_PAINEL`
  (status, ids da lista, da paginação e do aviso de vazio, e texto de vazio)
  e `acoesDoAnuncio(status)` com as ações de cada situação (RN1).
- `front/js/adaptadores/ads_api.js`: `alterarStatus(id, status)` chama
  `PATCH /api/ads/<id>/status`.
- `front/meus-anuncios/index.html`: seção "Vendidos".
- `front/js/paginas/meus_anuncios.js`: carrega as três seções a partir de
  `SECOES_DO_PAINEL`, monta os botões com `acoesDoAnuncio` e liga "Marcar como
  vendido" e "Reativar" com confirmação; depois de cada ação, recarrega as
  três listas.

## Estratégia de testes

- `front/tests/meus_anuncios.test.js`: ações por situação; o painel pede as
  três listas; "Marcar como vendido" confirmado chama o `PATCH` e recarrega;
  cancelado não chama nada.
- Teste no navegador com a conta demo (CA1–CA5).
