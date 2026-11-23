import test from "node:test";
import assert from "node:assert/strict";
import {
  ROTAS,
  rotaDetalhes,
  rotaEditarAnuncio,
} from "../js/dominio/rotas.js";

test("ROTAS lista todas as telas do front", () => {
  assert.deepEqual(ROTAS, {
    entrar: "/entrar/",
    cadastro: "/cadastro/",
    inicio: "/inicio/",
    perfil: "/perfil/",
    editarPerfilAnunciante: "/perfil/anunciante/",
    novoAnuncio: "/anuncios/novo/",
    detalhes: "/anuncios/detalhes/",
    meusAnuncios: "/meus-anuncios/",
  });
});

test("rotaDetalhes monta o endereço dos detalhes com o id", () => {
  assert.equal(rotaDetalhes(7), "/anuncios/detalhes/?id=7");
});

test("rotaDetalhes escapa o id", () => {
  assert.equal(rotaDetalhes("a&b"), "/anuncios/detalhes/?id=a%26b");
});

test("rotaEditarAnuncio monta o endereço de edição com o id", () => {
  assert.equal(rotaEditarAnuncio(12), "/anuncios/novo/?editar=12");
});

test("rotaEditarAnuncio escapa o id", () => {
  assert.equal(rotaEditarAnuncio("1 2"), "/anuncios/novo/?editar=1%202");
});
