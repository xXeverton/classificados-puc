import assert from "node:assert/strict";
import test from "node:test";
import {
  carregarAnuncioParaEdicao,
  mapearAnuncioParaFormulario,
} from "../js/fluxos/anuncio_edicao.js";

test("busca anúncio expirado e mapeia seus dados para edição", async () => {
  const chamadas = [];
  const anuncio = {
    id: 8,
    title: "Livro de cálculo",
    type: "product",
    category: "Livros",
    description: "Livro usado em bom estado.",
    estado_conservacao: "usado_regular",
    preco_a_combinar: false,
    price: 42.5,
    image_url: "http://localhost:5000/media/livro.webp",
  };
  const deps = {
    adsApi: {
      listarMeus: async (status) => {
        chamadas.push(status);
        return {
          status: 200,
          corpo: {
            items: status === "expired" ? [anuncio] : [],
          },
        };
      },
    },
  };

  const resultado = await carregarAnuncioParaEdicao(deps, "8");

  assert.deepEqual(chamadas, ["published", "expired"]);
  assert.deepEqual(resultado, { tipo: "carregado", anuncio });
  assert.deepEqual(mapearAnuncioParaFormulario(anuncio), {
    titulo: "Livro de cálculo",
    categoria: "produto",
    descricao: "Livro usado em bom estado.",
    estadoConservacao: "usado_regular",
    precoACombinar: false,
    semPreco: false,
    preco: "42,5",
    imageUrl: "http://localhost:5000/media/livro.webp",
    dataEvento: "",
    horarioEvento: "",
    localEvento: "",
  });
});

test("mapeia data, horário e local do evento para edição", () => {
  assert.deepEqual(
    mapearAnuncioParaFormulario({
      id: 3,
      title: "Feira de profissões",
      type: "event",
      description: "Venha conhecer.",
      preco_a_combinar: true,
      data_evento: "2026-12-05",
      horario_evento: "19:30",
      local_evento: "Auditório",
    }),
    {
      titulo: "Feira de profissões",
      categoria: "evento",
      descricao: "Venha conhecer.",
      estadoConservacao: "",
      precoACombinar: true,
      semPreco: false,
      preco: "",
      imageUrl: undefined,
      dataEvento: "2026-12-05",
      horarioEvento: "19:30",
      localEvento: "Auditório",
    },
  );
});

test("busca anúncio publicado em uma página posterior", async () => {
  const chamadas = [];
  const anuncio = {
    id: 21,
    title: "Livro de álgebra",
    type: "product",
    category: "Livros",
  };
  const deps = {
    adsApi: {
      listarMeus: async (status, page) => {
        chamadas.push(`${status}:${page}`);
        return {
          status: 200,
          corpo: {
            items: status === "published" && page === 2 ? [anuncio] : [],
            total_pages: status === "published" ? 2 : 0,
          },
        };
      },
    },
  };

  const resultado = await carregarAnuncioParaEdicao(deps, 21);

  assert.deepEqual(chamadas, ["published:1", "published:2"]);
  assert.deepEqual(resultado, { tipo: "carregado", anuncio });
});

test("evento sem preço volta marcado para edição", () => {
  const valores = mapearAnuncioParaFormulario({
    id: 4,
    title: "Palestra aberta",
    type: "event",
    sem_preco: true,
    preco_a_combinar: false,
    price: null,
  });
  assert.equal(valores.semPreco, true);
  assert.equal(valores.precoACombinar, false);
  assert.equal(valores.preco, "");
});
