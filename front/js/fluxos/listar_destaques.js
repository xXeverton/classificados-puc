import { limitarDestaques } from "../dominio/destaques.js";
import { chamarApi } from "./conexao.js";

// Os destaques são um extra do início: qualquer falha só esconde o painel e
// nunca impede o feed (CA22). Sessão inválida é tratada pelo feed.
export async function listarDestaques(deps) {
  let chamada;
  try {
    chamada = await chamarApi(() => deps.adsApi.listarDestaques());
  } catch {
    return { tipo: "indisponivel", eventos: [] };
  }
  const { resposta, falha } = chamada;
  if (falha || resposta.status !== 200) {
    return { tipo: "indisponivel", eventos: [] };
  }
  return { tipo: "destaques", eventos: limitarDestaques(resposta.corpo?.items) };
}
