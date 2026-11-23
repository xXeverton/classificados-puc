// Regras do painel de eventos em destaque do início (spec 015). Sem DOM.

import { contarFiltrosAtivos } from "./feed.js";
import { rotaDetalhes } from "./rotas.js";

export const INTERVALO_CARROSSEL_MS = 6000;

// O painel só aparece quando não há busca nem filtro (CA20). O mesmo critério
// tira os eventos dos cards de baixo: eles ficam só no painel (CA21).
export function deveMostrarDestaques(params) {
  return !params.search && contarFiltrosAtivos(params) === 0;
}

export function temCarrossel(total) {
  return total > 1;
}

export function proximoIndice(atual, total) {
  if (total <= 0) return 0;
  return (atual + 1) % total;
}

export function indiceAnterior(atual, total) {
  if (total <= 0) return 0;
  return (atual - 1 + total) % total;
}

export function rotuloDoSlide(indice, total) {
  return `Evento ${indice + 1} de ${total}`;
}

// Recebe "AAAA-MM-DD" da API e devolve "DD/MM/AAAA" sem passar por Date, que
// deslocaria o dia conforme o fuso do navegador.
export function formatarDataDoEvento(data) {
  const partes = /^(\d{4})-(\d{2})-(\d{2})$/.exec(data ?? "");
  if (!partes) return "";
  return `${partes[3]}/${partes[2]}/${partes[1]}`;
}

// "19:30" na tela de detalhes; vazio quando o evento não tem horário.
export function formatarHorarioDoEvento(horario) {
  return /^\d{2}:\d{2}$/.test(horario ?? "") ? horario : "";
}

export function dadosDoDestaque(anuncio) {
  return {
    id: anuncio.id,
    titulo: anuncio.title,
    imagem: anuncio.image_url ?? null,
    data: formatarDataDoEvento(anuncio.data_evento),
    detalhesUrl: rotaDetalhes(anuncio.id),
  };
}

// A API devolve até 5; o front não confia nisso para não quebrar o layout.
export function limitarDestaques(itens, limite = 5) {
  return Array.isArray(itens) ? itens.slice(0, limite) : [];
}
