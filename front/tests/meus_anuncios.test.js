import assert from "node:assert/strict";
import test from "node:test";

import {
  SECOES_DO_PAINEL,
  acoesDoAnuncio,
} from "../js/dominio/meus_anuncios.js";

class ElementoFalso {
  constructor() {
    this.children = [];
    this.hidden = false;
    this.handlers = {};
  }

  append(...elementos) {
    this.children.push(...elementos);
  }

  prepend(...elementos) {
    this.children.unshift(...elementos);
  }

  setAttribute() {}

  querySelector() {
    this.conteudo ??= new ElementoFalso();
    return this.conteudo;
  }

  replaceChildren(...elementos) {
    this.children = [...elementos];
  }

  addEventListener(evento, handler) {
    this.handlers[evento] = handler;
  }
}

function procurarPorTexto(elemento, texto) {
  if (elemento.textContent === texto) return elemento;
  for (const filho of elemento.children ?? []) {
    const achado = procurarPorTexto(filho, texto);
    if (achado) return achado;
  }
  return null;
}

const SELETORES = [
  "#alerta",
  "#conteudo",
  "[data-cabecalho]",
  ...SECOES_DO_PAINEL.flatMap((secao) => [
    `#${secao.lista}`,
    `#${secao.paginacao}`,
    `#${secao.vazio}`,
  ]),
];

async function abrirPainel({ anuncios, confirmar = true }) {
  const anteriores = new Map(
    ["document", "location", "window"].map((nome) => [
      nome,
      Object.getOwnPropertyDescriptor(globalThis, nome),
    ]),
  );
  const elementos = new Map(
    SELETORES.map((seletor) => [seletor, new ElementoFalso()]),
  );
  elementos.get("#conteudo").hidden = true;
  const requisicoes = [];
  const resposta = (corpo, status = 200) => ({
    status,
    redirected: false,
    json: async () => corpo,
  });
  const janela = {
    confirm: () => confirmar,
    localStorage: {
      getItem: () => JSON.stringify({
        token: "token-teste",
        expira_em: new Date(Date.now() + 60_000).toISOString(),
      }),
    },
    location: {
      origin: "http://localhost:5173",
      pathname: "/meus-anuncios/",
      search: "",
      replace() {},
    },
    fetch: async (url, opcoes = {}) => {
      const destino = new URL(url);
      const metodo = opcoes.method ?? "GET";
      requisicoes.push({
        metodo,
        caminho: destino.pathname + destino.search,
        corpo: opcoes.body ? JSON.parse(opcoes.body) : undefined,
      });
      if (destino.pathname === "/auth/me") {
        return resposta({ nome_usuario: "demo-classificados" });
      }
      const status = /^\/api\/ads\/(\d+)\/status$/.exec(destino.pathname);
      if (status && metodo === "PATCH") {
        const anuncio = anuncios.find((ad) => ad.id === Number(status[1]));
        anuncio.status = JSON.parse(opcoes.body).status;
        return resposta(anuncio);
      }
      if (destino.pathname === "/api/ads") {
        const items = anuncios.filter(
          (ad) => ad.status === destino.searchParams.get("status"),
        );
        return resposta({
          items,
          page: 1,
          total_pages: 1,
          total_items: items.length,
        });
      }
      return resposta({}, 404);
    },
  };

  Object.defineProperty(globalThis, "document", {
    configurable: true,
    value: {
      createElement: () => new ElementoFalso(),
      querySelector: (seletor) => elementos.get(seletor),
    },
  });
  Object.defineProperty(globalThis, "location", {
    configurable: true,
    value: janela.location,
  });
  Object.defineProperty(globalThis, "window", {
    configurable: true,
    value: janela,
  });

  const restaurar = () => {
    for (const [nome, descritor] of anteriores) {
      if (descritor) Object.defineProperty(globalThis, nome, descritor);
      else delete globalThis[nome];
    }
  };
  try {
    await import(`../js/paginas/meus_anuncios.js?teste=${Math.random()}`);
  } catch (erro) {
    restaurar();
    throw erro;
  }
  return { elementos, requisicoes, restaurar };
}

const anuncio = (id, title, status) => ({
  id,
  title,
  status,
  category: "produto",
  image_url: null,
  preco_a_combinar: false,
  price: 25,
});

test("cada situação mostra as ações certas", () => {
  assert.deepEqual(
    acoesDoAnuncio("published").map((acao) => acao.tipo),
    ["detalhes", "editar", "vender", "excluir"],
  );
  assert.deepEqual(
    acoesDoAnuncio("expired").map((acao) => acao.tipo),
    ["editar", "vender", "renovar", "excluir"],
  );
  assert.deepEqual(
    acoesDoAnuncio("sold").map((acao) => acao.tipo),
    ["reativar", "excluir"],
  );
  assert.deepEqual(acoesDoAnuncio("desconhecido"), []);
});

test('"Ver detalhes" só aparece em anúncios publicados (RN5)', () => {
  for (const status of ["expired", "sold", "desconhecido"]) {
    assert.ok(
      !acoesDoAnuncio(status).some((acao) => acao.tipo === "detalhes"),
      status,
    );
  }
  const detalhes = acoesDoAnuncio("published")[0];
  assert.equal(detalhes.rotulo, "Ver detalhes");
  assert.equal(detalhes.estilo, "contorno");
});

test("o painel tem as seções publicados, expirados e vendidos", () => {
  assert.deepEqual(
    SECOES_DO_PAINEL.map((secao) => secao.status),
    ["published", "expired", "sold"],
  );
});

test("carrega e exibe as três listas da API", async () => {
  const painel = await abrirPainel({
    anuncios: [
      anuncio(1, "Anúncio publicado", "published"),
      anuncio(2, "Anúncio expirado", "expired"),
      anuncio(3, "Anúncio vendido", "sold"),
    ],
  });
  try {
    const { elementos, requisicoes } = painel;
    assert.equal(elementos.get("#conteudo").hidden, false);
    assert.equal(elementos.get("#publicados").children.length, 1);
    assert.equal(elementos.get("#expirados").children.length, 1);
    assert.equal(elementos.get("#vendidos").children.length, 1);
    assert.deepEqual(
      requisicoes
        .filter((req) => req.caminho.startsWith("/api/ads"))
        .map((req) => req.caminho),
      [
        "/api/ads?owner=me&status=published&page=1",
        "/api/ads?owner=me&status=expired&page=1",
        "/api/ads?owner=me&status=sold&page=1",
      ],
    );
  } finally {
    painel.restaurar();
  }
});

test("marcar como vendido chama a API e move o anúncio", async () => {
  const painel = await abrirPainel({
    anuncios: [anuncio(1, "Livro", "published")],
  });
  try {
    const { elementos, requisicoes } = painel;
    const botao = procurarPorTexto(
      elementos.get("#publicados"),
      "Marcar como vendido",
    );
    assert.ok(botao, "botão Marcar como vendido não encontrado");

    await botao.handlers.click();

    const patch = requisicoes.find((req) => req.metodo === "PATCH");
    assert.deepEqual(patch, {
      metodo: "PATCH",
      caminho: "/api/ads/1/status",
      corpo: { status: "sold" },
    });
    assert.equal(elementos.get("#publicados").children.length, 0);
    assert.equal(elementos.get("#vendidos").children.length, 1);
    assert.equal(elementos.get("#alerta").className, "alerta alerta--sucesso");
  } finally {
    painel.restaurar();
  }
});

test("reativar um vendido chama a API com published", async () => {
  const painel = await abrirPainel({
    anuncios: [anuncio(3, "Bicicleta", "sold")],
  });
  try {
    const { elementos, requisicoes } = painel;
    const botao = procurarPorTexto(elementos.get("#vendidos"), "Reativar");
    assert.ok(botao, "botão Reativar não encontrado");
    assert.equal(
      procurarPorTexto(elementos.get("#vendidos"), "Editar"),
      null,
    );

    await botao.handlers.click();

    const patch = requisicoes.find((req) => req.metodo === "PATCH");
    assert.deepEqual(patch.corpo, { status: "published" });
    assert.equal(elementos.get("#publicados").children.length, 1);
    assert.equal(elementos.get("#vendidos").children.length, 0);
  } finally {
    painel.restaurar();
  }
});

test("cancelar a confirmação não chama a API", async () => {
  const painel = await abrirPainel({
    anuncios: [anuncio(1, "Livro", "published")],
    confirmar: false,
  });
  try {
    const { elementos, requisicoes } = painel;
    const botao = procurarPorTexto(
      elementos.get("#publicados"),
      "Marcar como vendido",
    );

    await botao.handlers.click();

    assert.equal(requisicoes.some((req) => req.metodo === "PATCH"), false);
    assert.equal(elementos.get("#publicados").children.length, 1);
  } finally {
    painel.restaurar();
  }
});
