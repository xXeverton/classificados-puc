import test from "node:test";
import assert from "node:assert/strict";

import {
  gerarLinkWhatsapp,
  normalizarNumeroWhatsapp,
} from "../js/dominio/link_whatsapp.js";

test("normaliza numero brasileiro com mascara e adiciona 55", () => {
  assert.equal(normalizarNumeroWhatsapp("(21) 98765-4321"), "5521987654321");
});

test("nao duplica codigo 55 em numero internacional", () => {
  assert.equal(normalizarNumeroWhatsapp("+55 21 98765-4321"), "5521987654321");
  assert.equal(normalizarNumeroWhatsapp("55 (21) 98765-4321"), "5521987654321");
});

test("preserva DDI explicito de numero mundial", () => {
  assert.equal(normalizarNumeroWhatsapp("+1 (202) 555-0123"), "12025550123");
  assert.equal(normalizarNumeroWhatsapp("00 44 20 7946 0958"), "442079460958");
});

test("gera link com mensagem contendo o titulo e parametros codificados", () => {
  const link = gerarLinkWhatsapp(
    "(21) 98765-4321",
    "Fogão 4 bocas & forno – 50% off",
  );

  assert.equal(
    link,
    "https://wa.me/5521987654321?text=" +
      encodeURIComponent(
        "Olá! Vi seu anúncio Fogão 4 bocas & forno – 50% off no PUC pra Rolo e tenho interesse.",
      ),
  );
});

test("usa mensagem generica para titulo vazio ou apenas espacos", () => {
  const esperado = "https://wa.me/5521987654321?text=" + encodeURIComponent(
    "Olá! Vi seu anúncio no PUC pra Rolo e tenho interesse.",
  );

  assert.equal(gerarLinkWhatsapp("(21) 98765-4321", ""), esperado);
  assert.equal(gerarLinkWhatsapp("(21) 98765-4321", "   "), esperado);
});

test("preserva titulo longo sem truncamento", () => {
  const titulo = "A".repeat(300);
  const link = gerarLinkWhatsapp("(21) 98765-4321", titulo);

  assert.ok(link.includes(encodeURIComponent(titulo)));
});

test("retorna null para numero ausente ou fora de 8 a 15 digitos", () => {
  assert.equal(gerarLinkWhatsapp("", "Bicicleta"), null);
  assert.equal(gerarLinkWhatsapp("sem numero", "Bicicleta"), null);
  assert.equal(gerarLinkWhatsapp("1234567", "Bicicleta"), null);
  assert.equal(gerarLinkWhatsapp("1234567890123456", "Bicicleta"), null);
});

test("usa o numero recebido em cada chamada sem cache", () => {
  assert.ok(
    gerarLinkWhatsapp("(21) 98765-4321", "Bicicleta").startsWith(
      "https://wa.me/5521987654321?",
    ),
  );
  assert.ok(
    gerarLinkWhatsapp("+1 (202) 555-0123", "Mesa").startsWith(
      "https://wa.me/12025550123?",
    ),
  );
});
