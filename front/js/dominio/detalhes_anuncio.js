import {
  gerarLinkWhatsapp,
  gerarMensagemWhatsapp,
} from "./link_whatsapp.js";

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
    whatsapp: "Chamar no WhatsApp",
    telefone: "Telefone",
    email: "Enviar E-mail",
    site: "Site",
    link: contato.rotulo || "Link",
  }[contato.tipo] || contato.rotulo || contato.valor;
}

export function resolverUrlRecurso(url, apiBaseUrl) {
  if (!url) return null;
  if (/^https?:\/\//i.test(url)) return url;
  return `${apiBaseUrl}${url}`;
}

export function gerarLinkEmailContato(endereco, titulo) {
  if (typeof endereco !== "string" || !endereco.trim()) return null;

  const assunto = `Interesse no anúncio: ${titulo || ""}`;
  const corpo = typeof titulo === "string" && titulo.trim()
    ? `Olá! Tenho interesse no anúncio ${titulo.trim()} no PUC pra Rolo.`
    : "Olá! Tenho interesse neste anúncio no PUC pra Rolo.";
  return `mailto:${endereco.trim()}?subject=${encodeURIComponent(assunto)}&body=${encodeURIComponent(corpo)}`;
}

export function hrefContato(contato, titulo) {
  if (contato.tipo === "whatsapp") {
    if (contato.link_de_conversa) {
      const separador = contato.link_de_conversa.includes("?") ? "&" : "?";
      const mensagem = encodeURIComponent(gerarMensagemWhatsapp(titulo));
      return `${contato.link_de_conversa}${separador}text=${mensagem}`;
    }
    const numero = contato.codigo_pais
      ? `${contato.codigo_pais}${contato.valor || ""}`
      : contato.valor;
    return gerarLinkWhatsapp(numero, titulo);
  }
  if (contato.tipo === "telefone") {
    return `tel:${contato.codigo_pais}${contato.valor}`;
  }
  if (contato.tipo === "email") {
    return gerarLinkEmailContato(contato.valor, titulo);
  }
  return contato.valor;
}
