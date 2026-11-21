import test from "node:test";
import assert from "node:assert/strict";
import { CODIGO_PAIS_PADRAO, PAISES, PAIS_PADRAO, textoDoPais } from "../js/dominio/codigos_paises.js";

test("Brasil (+55) é o padrão e o primeiro da lista", () => {
  assert.equal(PAIS_PADRAO.nome, "Brasil");
  assert.equal(CODIGO_PAIS_PADRAO, "55");
  assert.equal(PAISES[0], PAIS_PADRAO);
});

test("códigos têm de 1 a 3 dígitos e não se repetem", () => {
  const codigos = PAISES.map((p) => p.codigo);
  assert.ok(codigos.every((c) => /^\d{1,3}$/.test(c)));
  assert.equal(new Set(codigos).size, codigos.length);
});

test("texto do país mostra nome e código", () => {
  assert.equal(textoDoPais(PAIS_PADRAO), "Brasil (+55)");
});
