const CODIGO_PAIS_BRASIL = "55";
const TAMANHO_MINIMO_NUMERO = 8;
const TAMANHO_MAXIMO_NUMERO = 15;

const MENSAGEM_COM_TITULO =
  "Olá! Vi seu anúncio {titulo} no PUC pra Rolo e tenho interesse.";
const MENSAGEM_SEM_TITULO =
  "Olá! Vi seu anúncio no PUC pra Rolo e tenho interesse.";

export function normalizarNumeroWhatsapp(numero) {
  if (typeof numero !== "string") return null;

  const entrada = numero.trim();
  if (!entrada) return null;

  let digitos = entrada.replace(/\D/g, "");
  if (!digitos) return null;

  const ddiExplicito = entrada.startsWith("+") || entrada.startsWith("00");
  if (ddiExplicito && entrada.startsWith("00")) {
    digitos = digitos.slice(2);
  }

  if (
    digitos.length < TAMANHO_MINIMO_NUMERO ||
    digitos.length > TAMANHO_MAXIMO_NUMERO
  ) {
    return null;
  }

  if (!ddiExplicito && !digitos.startsWith(CODIGO_PAIS_BRASIL)) {
    digitos = `${CODIGO_PAIS_BRASIL}${digitos}`;
  }

  if (
    digitos.length < TAMANHO_MINIMO_NUMERO ||
    digitos.length > TAMANHO_MAXIMO_NUMERO
  ) {
    return null;
  }

  return digitos;
}

export function gerarLinkWhatsapp(numero, titulo) {
  const numeroNormalizado = normalizarNumeroWhatsapp(numero);
  if (!numeroNormalizado) return null;

  const tituloLimpo =
    typeof titulo === "string" ? titulo.trim() : "";
  const mensagem = tituloLimpo
    ? MENSAGEM_COM_TITULO.replace("{titulo}", tituloLimpo)
    : MENSAGEM_SEM_TITULO;

  return `https://wa.me/${numeroNormalizado}?text=${encodeURIComponent(mensagem)}`;
}
