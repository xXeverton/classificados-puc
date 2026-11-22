const TIPOS = new Set(["all", "product", "service", "event"]);
// Digits with an optional decimal part; comma or dot as separator.
const FORMATO_PRECO = /^\d+([.,]\d+)?$/;

export const MENSAGEM_FILTROS_SEM_RESULTADO =
  "Nenhum anúncio encontrado com esses filtros.";
const MENSAGEM_FEED_VAZIO = "Nenhum anúncio publicado encontrado.";

function converterPreco(texto) {
  const valor = String(texto ?? "").trim();
  if (!FORMATO_PRECO.test(valor)) return null;
  return Number(valor.replace(",", "."));
}

export function paramsSemFiltros() {
  return { page: 1, search: "", type: "all", minPrice: null, maxPrice: null };
}

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
    minPrice: converterPreco(parametros.get("min_price")),
    maxPrice: converterPreco(parametros.get("max_price")),
  };
}

export function montarParametrosFeed({
  page = 1,
  search = "",
  type = "all",
  minPrice = null,
  maxPrice = null,
}) {
  const parametros = new URLSearchParams();
  parametros.set("page", String(page));
  if (search) parametros.set("search", search);
  if (TIPOS.has(type) && type !== "all") parametros.set("type", type);
  if (minPrice !== null) parametros.set("min_price", String(minPrice));
  if (maxPrice !== null) parametros.set("max_price", String(maxPrice));
  return parametros;
}

export function lerFaixaDePreco(textoMinimo, textoMaximo) {
  const limites = [
    ["minPrice", textoMinimo, "Preço mínimo"],
    ["maxPrice", textoMaximo, "Preço máximo"],
  ];
  const faixa = {};
  for (const [campo, texto, rotulo] of limites) {
    if (!String(texto ?? "").trim()) {
      faixa[campo] = null;
      continue;
    }
    const valor = converterPreco(texto);
    if (valor === null) {
      return { erro: `${rotulo} deve ser um número maior ou igual a zero.` };
    }
    faixa[campo] = valor;
  }
  if (
    faixa.minPrice !== null
    && faixa.maxPrice !== null
    && faixa.minPrice > faixa.maxPrice
  ) {
    return { erro: "Preço mínimo não pode ser maior que o máximo." };
  }
  return faixa;
}

export function contarFiltrosAtivos({ type = "all", minPrice = null, maxPrice = null }) {
  return [type !== "all", minPrice !== null, maxPrice !== null]
    .filter(Boolean).length;
}

export function mensagemDeFeedVazio(params, mensagemDaApi) {
  if (params.search || contarFiltrosAtivos(params) > 0) {
    return MENSAGEM_FILTROS_SEM_RESULTADO;
  }
  return mensagemDaApi || MENSAGEM_FEED_VAZIO;
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
