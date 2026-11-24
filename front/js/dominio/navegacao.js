// Itens do cabeçalho único das telas com login (D-035). Sem DOM.

import { ROTAS } from "./rotas.js";

export const ITENS_DO_CABECALHO = Object.freeze([
  Object.freeze({ chave: "inicio", rotulo: "Início", rota: ROTAS.inicio }),
  Object.freeze({
    chave: "meus-anuncios",
    rotulo: "Meus anúncios",
    rota: ROTAS.meusAnuncios,
  }),
  Object.freeze({ chave: "perfil", rotulo: "Meu perfil", rota: ROTAS.perfil }),
]);

export const BOTAO_NOVO_ANUNCIO = Object.freeze({
  chave: "novo-anuncio",
  rotulo: "Novo anúncio",
  rota: ROTAS.novoAnuncio,
});

const CHAVE_POR_CAMINHO = Object.freeze({
  [ROTAS.inicio]: "inicio",
  [ROTAS.meusAnuncios]: "meus-anuncios",
  [ROTAS.perfil]: "perfil",
  [ROTAS.editarPerfilAnunciante]: "perfil",
});

function normalizar(caminho) {
  const semArquivo = String(caminho ?? "").replace(/index\.html$/, "");
  if (!semArquivo) return "";
  return semArquivo.endsWith("/") ? semArquivo : `${semArquivo}/`;
}

// Devolve a chave do item (ou do botão) que representa a tela atual, ou null.
export function itemAtual(caminho, busca = "") {
  const normalizado = normalizar(caminho);
  if (normalizado === ROTAS.novoAnuncio) {
    // Na edição, quem navega é o painel; só a criação marca o botão.
    return new URLSearchParams(busca).has("editar")
      ? null
      : BOTAO_NOVO_ANUNCIO.chave;
  }
  return CHAVE_POR_CAMINHO[normalizado] ?? null;
}
