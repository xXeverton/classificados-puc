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
  classificarContatosPrincipais,
  rotaEdicaoDoDono,
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

test("contact availability includes WhatsApp and email when both are valid", () => {
  const estado = classificarContatosPrincipais([
    { tipo: "whatsapp", codigo_pais: "55", valor: "(21) 98765-4321" },
    { tipo: "email", valor: "vendedor@puc-rio.br" },
  ], "Bicicleta");

  assert.equal(estado.whatsapp, "https://wa.me/5521987654321?text=" +
    encodeURIComponent(
      "Olá! Vi seu anúncio Bicicleta no PUC pra Rolo e tenho interesse.",
    ));
  assert.ok(estado.email.startsWith("mailto:vendedor@puc-rio.br?"));
});

test("contact availability hides missing WhatsApp or email", () => {
  const somenteEmail = classificarContatosPrincipais([
    { tipo: "email", valor: "vendedor@puc-rio.br" },
  ], "Mesa");
  assert.equal(somenteEmail.whatsapp, null);
  assert.ok(somenteEmail.email);

  const somenteWhatsapp = classificarContatosPrincipais([
    { tipo: "whatsapp", codigo_pais: "55", valor: "(21) 98765-4321" },
  ], "Mesa");
  assert.ok(somenteWhatsapp.whatsapp);
  assert.equal(somenteWhatsapp.email, null);
});

test("invalid WhatsApp is absent while valid email remains available", () => {
  const estado = classificarContatosPrincipais([
    { tipo: "whatsapp", codigo_pais: "55", valor: "123" },
    { tipo: "email", valor: "vendedor@puc-rio.br" },
  ], "Mesa");

  assert.equal(estado.whatsapp, null);
  assert.ok(estado.email);
});

test("both unavailable returns no active links", () => {
  const estado = classificarContatosPrincipais([
    { tipo: "whatsapp", codigo_pais: "55", valor: "123" },
    { tipo: "email", valor: "email-invalido" },
  ], "Mesa");

  assert.equal(estado.whatsapp, null);
  assert.equal(estado.email, null);
});

test("contact availability uses updated profile data on every call", () => {
  const antes = classificarContatosPrincipais([
    { tipo: "email", valor: "antes@puc-rio.br" },
  ], "Mesa");
  const depois = classificarContatosPrincipais([
    { tipo: "whatsapp", codigo_pais: "55", valor: "(21) 98765-4321" },
  ], "Mesa");

  assert.ok(antes.email);
  assert.equal(antes.whatsapp, null);
  assert.ok(depois.whatsapp);
  assert.equal(depois.email, null);
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

test("o dono recebe a rota de edição do anúncio (CA9)", () => {
  assert.equal(
    rotaEdicaoDoDono({ ad: { id: 5 }, is_owner: true }),
    "/anuncios/novo/?editar=5",
  );
});

test("quem não é o dono não recebe rota de edição (CA10)", () => {
  assert.equal(rotaEdicaoDoDono({ ad: { id: 5 }, is_owner: false }), null);
  assert.equal(rotaEdicaoDoDono({ ad: { id: 5 } }), null);
  assert.equal(rotaEdicaoDoDono(null), null);
});
