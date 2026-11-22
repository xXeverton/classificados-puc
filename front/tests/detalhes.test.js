import test from "node:test";
import assert from "node:assert/strict";

import {
  idDoAnuncio,
  formatarPrecoDetalhes,
  rotuloConservacao,
  rotuloContato,
  resolverUrlRecurso,
  gerarLinkEmailContato,
  hrefContato,
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

test("WhatsApp and email use the requested contact button labels", () => {
  assert.equal(
    rotuloContato({ tipo: "whatsapp", valor: "21999999999" }),
    "Chamar no WhatsApp",
  );
  assert.equal(
    rotuloContato({ tipo: "email", valor: "vendedor@puc-rio.br" }),
    "Enviar E-mail",
  );
});

test("email link includes encoded recipient, subject and body", () => {
  const link = gerarLinkEmailContato(
    "vendedor@puc-rio.br",
    "Fogão & forno – 50%",
  );

  assert.ok(link.startsWith("mailto:vendedor@puc-rio.br?"));
  assert.ok(link.includes(
    "subject=" +
      encodeURIComponent("Interesse no anúncio: Fogão & forno – 50%"),
  ));
  assert.ok(link.includes(
    "body=" +
      encodeURIComponent(
        "Olá! Tenho interesse no anúncio Fogão & forno – 50% no PUC pra Rolo.",
      ),
  ));
});

test("WhatsApp contact link includes the announcement title", () => {
  const link = hrefContato(
    { tipo: "whatsapp", codigo_pais: "55", valor: "(21) 98765-4321" },
    "Bicicleta Caloi",
  );

  assert.equal(
    link,
    "https://wa.me/5521987654321?text=" +
      encodeURIComponent(
        "Olá! Vi seu anúncio Bicicleta Caloi no PUC pra Rolo e tenho interesse.",
      ),
  );
});

test("existing WhatsApp chat link receives the prefilled message", () => {
  const link = hrefContato(
    { tipo: "whatsapp", valor: "https://wa.me/5521987654321" },
    "Mesa & cadeiras",
  );

  assert.ok(link.startsWith("https://wa.me/5521987654321?text="));
  assert.ok(link.includes(encodeURIComponent("Mesa & cadeiras")));
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
