import test from "node:test";
import assert from "node:assert/strict";

import {
  idDoAnuncio,
  formatarPrecoDetalhes,
  rotuloConservacao,
  rotuloContato,
  resolverUrlRecurso,
} from "../js/dominio/detalhes_anuncio.js";

test("idDoAnuncio accepts only a positive integer", () => {
  assert.equal(idDoAnuncio("?id=12"), 12);
  assert.equal(idDoAnuncio("?id=abc"), null);
  assert.equal(idDoAnuncio("?id=0"), null);
});

test("detail price supports currency and negotiation", () => {
  assert.equal(formatarPrecoDetalhes(450.25, false), "R$ 450,25");
  assert.equal(formatarPrecoDetalhes(null, true), "A combinar");
});

test("conservation and contact labels are localized", () => {
  assert.equal(rotuloConservacao("novo"), "Novo");
  assert.equal(rotuloConservacao("usado_regular"), "Usado - regular");
  assert.equal(
    rotuloContato({ tipo: "link", rotulo: "Portfólio", valor: "https://example.com" }),
    "Portfólio",
  );
});

test("resource URLs use the API origin for protected and local media", () => {
  assert.equal(
    resolverUrlRecurso("/media/anuncios/foto.png", "http://127.0.0.1:5000"),
    "http://127.0.0.1:5000/media/anuncios/foto.png",
  );
  assert.equal(
    resolverUrlRecurso("https://cdn.example.com/foto.png", "http://127.0.0.1:5000"),
    "https://cdn.example.com/foto.png",
  );
});
