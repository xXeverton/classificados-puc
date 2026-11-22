import { montarUrlApi } from "../dominio/feed.js";

export function criarAdsApi(cliente) {
  return {
    listar: (params) => cliente.requisitar("GET", montarUrlApi(params)),
    detalhar: (id) => cliente.requisitar("GET", `/api/ads/${encodeURIComponent(id)}`),
    listarMeus: (status, page = 1) => cliente.requisitar(
      "GET",
      `/api/ads?owner=me&status=${status}&page=${page}`,
    ),
    publicar: (dados) => cliente.requisitar("POST", "/api/ads", dados),
    editar: (id, dados) => cliente.requisitar("PUT", `/api/ads/${id}`, dados),
    excluir: (id) => cliente.requisitar("DELETE", `/api/ads/${id}`),
    renovar: (id) => cliente.requisitar("POST", `/api/ads/${id}/renovar`),
  };
}
