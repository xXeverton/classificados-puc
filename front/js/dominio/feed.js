const TIPOS = new Set(["all", "product", "service", "event"]);

export function resumirDescricao(descricao, limite = 120) {
  if (!descricao) return null;
  const texto = String(descricao).trim();
  if (!texto) return null;
  if (texto.length <= limite) return texto;
  return `${texto.slice(0, limite - 3).trimEnd()}...`;
}

export function dadosDoCard(anuncio) {
  return {
    id: anuncio.id,
    titulo: anuncio.title,
    categoria: anuncio.category,
    preco: anuncio.price,
    data: anuncio.created_at,
    imagem: anuncio.image_url ?? null,
    tipo: anuncio.type,
    nomeAnunciante: anuncio.nome_anunciante ?? null,
    precoACombinar: anuncio.preco_a_combinar ?? false,
    descricaoResumida: anuncio.type === "service"
      ? resumirDescricao(anuncio.description)
      : null,
    detalhesUrl: `/anuncios/${encodeURIComponent(anuncio.id)}/`,
  };
}

export function parametrosDoFeed(parametros) {
  const paginaInformada = parametros.get("page");
  const pagina = Number(paginaInformada ?? 1);
  const busca = (parametros.get("search") ?? "").trim();
  const tipo = parametros.get("type") ?? "all";
  return {
    page: Number.isInteger(pagina) && pagina > 0 ? pagina : 1,
    search: busca,
    type: TIPOS.has(tipo) ? tipo : "all",
  };
}

export function montarParametrosFeed({ page = 1, search = "", type = "all" }) {
  const parametros = new URLSearchParams();
  parametros.set("page", String(page));
  if (search) parametros.set("search", search);
  if (TIPOS.has(type) && type !== "all") parametros.set("type", type);
  return parametros;
}

export function montarUrlApi(params) {
  return `/api/ads?${montarParametrosFeed(params).toString()}`;
}

export function paginasNumeradas(paginaAtual, totalPaginas) {
  if (totalPaginas <= 0) return [];
  if (totalPaginas <= 5) {
    return Array.from({ length: totalPaginas }, (_, indice) => indice + 1);
  }
  const inicio = Math.max(1, Math.min(paginaAtual - 2, totalPaginas - 4));
  return Array.from({ length: 5 }, (_, indice) => inicio + indice);
}
