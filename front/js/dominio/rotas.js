// Endereços das telas do front, em um só lugar (D-036). Sem DOM.

export const ROTAS = Object.freeze({
  entrar: "/entrar/",
  cadastro: "/cadastro/",
  inicio: "/inicio/",
  perfil: "/perfil/",
  editarPerfilAnunciante: "/perfil/anunciante/",
  novoAnuncio: "/anuncios/novo/",
  detalhes: "/anuncios/detalhes/",
  meusAnuncios: "/meus-anuncios/",
});

export function rotaDetalhes(id) {
  return `${ROTAS.detalhes}?id=${encodeURIComponent(id)}`;
}

export function rotaEditarAnuncio(id) {
  return `${ROTAS.novoAnuncio}?editar=${encodeURIComponent(id)}`;
}

// Cancelar a edição volta ao painel; cancelar a criação volta ao feed.
export function rotaAoCancelarAnuncio(idEmEdicao) {
  return idEmEdicao ? ROTAS.meusAnuncios : ROTAS.inicio;
}
