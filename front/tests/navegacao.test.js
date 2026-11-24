import test from "node:test";
import assert from "node:assert/strict";
import {
  BOTAO_NOVO_ANUNCIO,
  ITENS_DO_CABECALHO,
  itemAtual,
} from "../js/dominio/navegacao.js";

test("o menu tem Início, Meus anúncios e Meu perfil, nessa ordem (CA1)", () => {
  assert.deepEqual(
    ITENS_DO_CABECALHO.map(({ rotulo, rota }) => [rotulo, rota]),
    [
      ["Início", "/inicio/"],
      ["Meus anúncios", "/meus-anuncios/"],
      ["Meu perfil", "/perfil/"],
    ],
  );
});

test('"Novo anúncio" é um botão à parte, não um item do menu (CA5)', () => {
  assert.equal(BOTAO_NOVO_ANUNCIO.rotulo, "Novo anúncio");
  assert.equal(BOTAO_NOVO_ANUNCIO.rota, "/anuncios/novo/");
  assert.ok(!ITENS_DO_CABECALHO.some((i) => i.rotulo === "Anunciar"));
  assert.ok(!ITENS_DO_CABECALHO.some((i) => i.chave === BOTAO_NOVO_ANUNCIO.chave));
});

test("itemAtual marca início, meus anúncios e perfil (CA2)", () => {
  assert.equal(itemAtual("/inicio/"), "inicio");
  assert.equal(itemAtual("/meus-anuncios/"), "meus-anuncios");
  assert.equal(itemAtual("/perfil/"), "perfil");
});

test("o perfil de anunciante conta como Meu perfil (CA2)", () => {
  assert.equal(itemAtual("/perfil/anunciante/"), "perfil");
});

test("na criação de anúncio o marcado é o botão Novo anúncio (CA2)", () => {
  assert.equal(itemAtual("/anuncios/novo/"), "novo-anuncio");
  assert.equal(itemAtual("/anuncios/novo/", "?depois=anunciar"), "novo-anuncio");
});

test("na edição de anúncio nada é marcado (CA2)", () => {
  assert.equal(itemAtual("/anuncios/novo/", "?editar=5"), null);
});

test("nos detalhes do anúncio nada é marcado (CA2)", () => {
  assert.equal(itemAtual("/anuncios/detalhes/", "?id=3"), null);
});

test("itemAtual aceita o caminho sem barra final e com index.html", () => {
  assert.equal(itemAtual("/meus-anuncios"), "meus-anuncios");
  assert.equal(itemAtual("/perfil/index.html"), "perfil");
});

test("caminhos desconhecidos não marcam nada", () => {
  assert.equal(itemAtual("/outra/"), null);
  assert.equal(itemAtual(""), null);
});
