import test from "node:test";
import assert from "node:assert/strict";
import {
  INTERVALO_CARROSSEL_MS,
  dadosDoDestaque,
  deveMostrarDestaques,
  formatarDataDoEvento,
  formatarHorarioDoEvento,
  indiceAnterior,
  limitarDestaques,
  proximoIndice,
  rotuloDoSlide,
  temCarrossel,
} from "../js/dominio/destaques.js";
import { listarDestaques } from "../js/fluxos/listar_destaques.js";
import { paramsSemFiltros } from "../js/dominio/feed.js";
import { conexaoCaida, criarAdsApiFalsa } from "./fakes.js";

test("o carrossel troca a cada 6 segundos", () => {
  assert.equal(INTERVALO_CARROSSEL_MS, 6000);
});

test("o painel aparece só sem busca e sem filtros", () => {
  assert.equal(deveMostrarDestaques(paramsSemFiltros()), true);
  assert.equal(deveMostrarDestaques({ ...paramsSemFiltros(), search: "livro" }), false);
  assert.equal(deveMostrarDestaques({ ...paramsSemFiltros(), type: "event" }), false);
  assert.equal(deveMostrarDestaques({ ...paramsSemFiltros(), minPrice: 1 }), false);
  assert.equal(deveMostrarDestaques({ ...paramsSemFiltros(), maxPrice: 9 }), false);
  assert.equal(deveMostrarDestaques({ ...paramsSemFiltros(), page: 3 }), true);
});

test("só há carrossel com mais de um evento", () => {
  assert.equal(temCarrossel(0), false);
  assert.equal(temCarrossel(1), false);
  assert.equal(temCarrossel(2), true);
  assert.equal(temCarrossel(5), true);
});

test("o índice é circular nos dois sentidos", () => {
  assert.equal(proximoIndice(0, 3), 1);
  assert.equal(proximoIndice(2, 3), 0);
  assert.equal(indiceAnterior(1, 3), 0);
  assert.equal(indiceAnterior(0, 3), 2);
  assert.equal(proximoIndice(0, 0), 0);
  assert.equal(indiceAnterior(0, 0), 0);
});

test("o rótulo do slide conta a partir de 1", () => {
  assert.equal(rotuloDoSlide(0, 5), "Evento 1 de 5");
  assert.equal(rotuloDoSlide(4, 5), "Evento 5 de 5");
});

test("a data do evento não muda de dia com o fuso do navegador", () => {
  assert.equal(formatarDataDoEvento("2026-12-05"), "05/12/2026");
  assert.equal(formatarDataDoEvento("2026-01-01"), "01/01/2026");
  assert.equal(formatarDataDoEvento(null), "");
  assert.equal(formatarDataDoEvento("05/12/2026"), "");
  assert.equal(formatarDataDoEvento("2026-12-05T10:00:00Z"), "");
});

test("o horário só aparece no formato HH:MM", () => {
  assert.equal(formatarHorarioDoEvento("19:30"), "19:30");
  assert.equal(formatarHorarioDoEvento(null), "");
  assert.equal(formatarHorarioDoEvento("7h"), "");
});

test("dados do destaque trazem só imagem, título, data e link", () => {
  assert.deepEqual(
    dadosDoDestaque({
      id: 9,
      title: "Feira",
      image_url: "/media/a.png",
      data_evento: "2026-12-05",
      horario_evento: "10:00",
      local_evento: "Auditório",
    }),
    {
      id: 9,
      titulo: "Feira",
      imagem: "/media/a.png",
      data: "05/12/2026",
      detalhesUrl: "/anuncios/detalhes/?id=9",
    },
  );
  assert.equal(dadosDoDestaque({ id: 1, title: "x" }).imagem, null);
});

test("no máximo cinco destaques são usados", () => {
  assert.equal(limitarDestaques(Array.from({ length: 8 }, (_, i) => i)).length, 5);
  assert.deepEqual(limitarDestaques(undefined), []);
  assert.deepEqual(limitarDestaques("x"), []);
});

test("listar destaques devolve os eventos da API", async () => {
  const deps = {
    adsApi: {
      ...criarAdsApiFalsa(),
      listarDestaques: async () => ({ status: 200, corpo: { items: [{ id: 1 }, { id: 2 }] } }),
    },
  };
  const r = await listarDestaques(deps);
  assert.equal(r.tipo, "destaques");
  assert.deepEqual(r.eventos, [{ id: 1 }, { id: 2 }]);
});

test("falha ao listar destaques só deixa o painel indisponível", async () => {
  for (const resposta of [{ status: 500, corpo: {} }, { status: 401, corpo: {} }]) {
    const r = await listarDestaques({
      adsApi: { listarDestaques: async () => resposta },
    });
    assert.deepEqual(r, { tipo: "indisponivel", eventos: [] });
  }
  const offline = await listarDestaques({
    adsApi: { listarDestaques: async () => { throw conexaoCaida(); } },
  });
  assert.equal(offline.tipo, "indisponivel");
});
