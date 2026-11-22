export function idDoAnuncio(search) {
  const valor = new URLSearchParams(search).get("id");
  if (!valor) return null;
  if (!/^[1-9][0-9]*$/.test(valor)) return null;
  return Number(valor);
}

export function formatarPrecoDetalhes(valor, aCombinar) {
  if (aCombinar) return "A combinar";
  if (valor === null || valor === undefined) return "A combinar";
  return new Intl.NumberFormat("pt-BR", {
    style: "currency",
    currency: "BRL",
  }).format(valor);
}

export function rotuloConservacao(valor) {
  return {
    novo: "Novo",
    usado_regular: "Usado - regular",
  }[valor] ?? null;
}

export function rotuloContato(contato) {
  return {
    whatsapp: "WhatsApp",
    telefone: "Telefone",
    email: "E-mail",
    site: "Site",
    link: contato.rotulo || "Link",
  }[contato.tipo] || contato.rotulo || contato.valor;
}

export function resolverUrlRecurso(url, apiBaseUrl) {
  if (!url) return null;
  if (/^https?:\/\//i.test(url)) return url;
  return `${apiBaseUrl}${url}`;
}
