import test from "node:test";
import assert from "node:assert/strict";
import {
  contarCaracteres,
  montarPayloadAnuncio,
  normalizarPreco,
  validarAnuncio,
  validarFoto,
} from "../js/dominio/anuncio.js";

const anuncioBase = {
  titulo: "  Livro usado  ",
  categoria: "produto",
  estado_conservacao: "usado_regular",
  descricao: "  Em bom estado.  ",
  tipo_preco: "informar",
  preco: "12,5",
  imagem: null,
};

test("conta pontos de código Unicode e ignora espaços nas extremidades", () => {
  assert.equal(contarCaracteres("  📚abc  "), 4);
});

test("valida título inclusivo e descrição em pontos de código Unicode", () => {
  const noLimite = {
    ...anuncioBase,
    titulo: "📚".repeat(5),
    descricao: "📚".repeat(500),
  };
  assert.deepEqual(validarAnuncio(noLimite).erros, {});

  const acimaDoLimite = { ...noLimite, descricao: `${noLimite.descricao}📚` };
  assert.ok(validarAnuncio(acimaDoLimite).erros.descricao);
});

test("normaliza preços com vírgula ou ponto e rejeita valores fora do limite", () => {
  assert.equal(normalizarPreco(" 0012,5 "), "12.50");
  assert.equal(normalizarPreco("12.50"), "12.50");
  assert.equal(normalizarPreco("9999999999,99"), "9999999999.99");
  assert.equal(normalizarPreco("10000000000"), null);
  assert.equal(normalizarPreco("9".repeat(10000)), null);
  assert.equal(normalizarPreco("12,345"), null);
});

test("estado de conservação só é obrigatório para produto", () => {
  assert.ok(validarAnuncio({ ...anuncioBase, estado_conservacao: "" }).erros.estado_conservacao);
  assert.equal(
    validarAnuncio({ ...anuncioBase, categoria: "servico", estado_conservacao: "" })
      .erros.estado_conservacao,
    undefined,
  );
  assert.equal(
    validarAnuncio({ ...anuncioBase, categoria: "evento", estado_conservacao: "" })
      .erros.estado_conservacao,
    undefined,
  );
});

test("exige uma escolha explícita entre preço e A combinar", () => {
  assert.ok(validarAnuncio({ ...anuncioBase, tipo_preco: "" }).erros.tipo_preco);
});

test("monta payload só com os campos permitidos e preço decimal normalizado", () => {
  assert.deepEqual(montarPayloadAnuncio(anuncioBase), {
    titulo: "Livro usado",
    categoria: "produto",
    descricao: "Em bom estado.",
    preco_a_combinar: false,
    estado_conservacao: "usado_regular",
    preco: "12.50",
  });
  assert.deepEqual(
    montarPayloadAnuncio({
      ...anuncioBase,
      categoria: "evento",
      estado_conservacao: "",
      tipo_preco: "combinar",
    }),
    {
      titulo: "Livro usado",
      categoria: "evento",
      descricao: "Em bom estado.",
      preco_a_combinar: true,
    },
  );
});

test("valida foto única por tipo, tamanho e conteúdo", () => {
  assert.equal(validarFoto({ name: "foto.png", type: "image/png", size: 12 }), null);
  assert.match(
    validarFoto({ name: "foto.gif", type: "image/gif", size: 12 }),
    /JPG, PNG ou WebP/,
  );
  assert.match(
    validarFoto({ name: "foto.jpg", type: "image/jpeg", size: 5 * 1024 * 1024 + 1 }),
    /5 MB/,
  );
  assert.match(
    validarFoto({ name: "foto.jpg", type: "image/jpeg", size: 0 }),
    /vazia/,
  );
});
