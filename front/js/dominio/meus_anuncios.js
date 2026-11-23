// Regras do painel "Meus anúncios", sem DOM (specs 009 e 012).

export const SECOES_DO_PAINEL = Object.freeze([
  Object.freeze({
    status: "published",
    lista: "publicados",
    paginacao: "paginacao-publicados",
    vazio: "vazio-publicados",
    textoVazio: "Você ainda não possui anúncios publicados.",
  }),
  Object.freeze({
    status: "expired",
    lista: "expirados",
    paginacao: "paginacao-expirados",
    vazio: "vazio-expirados",
    textoVazio: "Você não possui anúncios expirados.",
  }),
  Object.freeze({
    status: "sold",
    lista: "vendidos",
    paginacao: "paginacao-vendidos",
    vazio: "vazio-vendidos",
    textoVazio: "Você não possui anúncios vendidos ou concluídos.",
  }),
]);

const DETALHES = { tipo: "detalhes", rotulo: "Ver detalhes", estilo: "contorno" };
const EDITAR = { tipo: "editar", rotulo: "Editar", estilo: "contorno" };
const VENDER = {
  tipo: "vender",
  rotulo: "Marcar como vendido",
  estilo: "contorno",
  confirmacao: "Marcar este anúncio como vendido? Ele sai do feed, "
    + "mas você pode reativá-lo depois.",
  novoStatus: "sold",
  sucesso: "Anúncio marcado como vendido.",
};
// Evento não se vende: o dono o encerra como concluído. Guarda o mesmo status
// "sold" da API, que tira o anúncio do feed e do painel (spec 015).
const CONCLUIR = {
  tipo: "concluir",
  rotulo: "Marcar como concluído",
  estilo: "contorno",
  confirmacao: "Marcar este evento como concluído? Ele sai do feed e dos "
    + "destaques, mas você pode reativá-lo depois.",
  novoStatus: "sold",
  sucesso: "Evento marcado como concluído.",
};
const RENOVAR = { tipo: "renovar", rotulo: "Renovar", estilo: "primario" };
const REATIVAR = {
  tipo: "reativar",
  rotulo: "Reativar",
  estilo: "primario",
  confirmacao: "Reativar este anúncio? Se o prazo de publicação já "
    + "acabou, ele volta como expirado e pode ser renovado.",
  novoStatus: "published",
  sucesso: "Anúncio reativado.",
};
const EXCLUIR = { tipo: "excluir", rotulo: "Excluir", estilo: "contorno" };

const ACOES_POR_STATUS = {
  published: [DETALHES, EDITAR, VENDER, EXCLUIR],
  expired: [EDITAR, VENDER, RENOVAR, EXCLUIR],
  sold: [REATIVAR, EXCLUIR],
};

// Evento não se renova (passada a data, o dono edita a data para publicá-lo
// de novo) e, em vez de "vendido", é marcado como concluído (spec 015, CA9).
export function acoesDoAnuncio(status, categoria) {
  const acoes = ACOES_POR_STATUS[status] ?? [];
  if (categoria === "evento") {
    return acoes
      .filter((acao) => acao.tipo !== RENOVAR.tipo)
      .map((acao) => (acao.tipo === VENDER.tipo ? CONCLUIR : acao));
  }
  return acoes;
}
