import { chamarApi } from "./conexao.js";

export async function carregarAnuncioParaEdicao(deps, id) {
  for (const status of ["published", "expired"]) {
    let pagina = 1;
    let totalPaginas = 1;
    while (pagina <= totalPaginas) {
      const { resposta, falha } = await chamarApi(
        () => deps.adsApi.listarMeus(status, pagina),
      );
      if (
        falha
        || resposta.status !== 200
        || !Array.isArray(resposta.corpo?.items)
      ) {
        return { tipo: "erro" };
      }

      const anuncio = resposta.corpo.items.find(
        (item) => String(item.id) === String(id),
      );
      if (anuncio) return { tipo: "carregado", anuncio };

      totalPaginas = resposta.corpo.total_pages ?? pagina;
      pagina += 1;
    }
  }
  return { tipo: "nao_encontrado" };
}

export function mapearAnuncioParaFormulario(anuncio) {
  return {
    titulo: anuncio.title,
    categoria: {
      product: "produto",
      service: "servico",
      event: "evento",
    }[anuncio.type] ?? "",
    descricao: anuncio.description ?? "",
    estadoConservacao: anuncio.estado_conservacao ?? "",
    precoACombinar: Boolean(anuncio.preco_a_combinar),
    preco: anuncio.price == null
      ? ""
      : String(anuncio.price).replace(".", ","),
    imageUrl: anuncio.image_url,
  };
}
