import { montarUrlApi } from "../dominio/feed.js";

export function criarAdsApi(cliente) {
  return {
    listar: (params) => cliente.requisitar("GET", montarUrlApi(params)),
    publicar: (dados) => cliente.requisitar("POST", "/api/ads", dados),
  };
}
