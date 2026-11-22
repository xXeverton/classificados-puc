import assert from "node:assert/strict";
import test from "node:test";

class ElementoFalso {
  constructor() {
    this.children = [];
    this.hidden = false;
    this.handlers = {};
  }

  append(...elementos) {
    this.children.push(...elementos);
  }

  replaceChildren(...elementos) {
    this.children = [...elementos];
  }

  addEventListener(evento, handler) {
    this.handlers[evento] = handler;
  }
}

test("carrega e exibe anúncios publicados e expirados da API", async () => {
  const anteriores = new Map(
    ["document", "location", "window"].map((nome) => [
      nome,
      Object.getOwnPropertyDescriptor(globalThis, nome),
    ]),
  );
  const elementos = new Map(
    [
      "#alerta",
      "#conteudo",
      "#sair",
      "#publicados",
      "#paginacao-publicados",
      "#vazio-publicados",
      "#expirados",
      "#paginacao-expirados",
      "#vazio-expirados",
    ].map((seletor) => [seletor, new ElementoFalso()]),
  );
  elementos.get("#conteudo").hidden = true;
  const requisicoes = [];
  const ad = (id, title) => ({
    id,
    title,
    category: "Livros",
    image_url: null,
    preco_a_combinar: false,
    price: 25,
  });
  const resposta = (corpo, status = 200) => ({
    status,
    redirected: false,
    json: async () => corpo,
  });
  const janela = {
    localStorage: {
      getItem: () => JSON.stringify({
        token: "token-teste",
        expira_em: new Date(Date.now() + 60_000).toISOString(),
      }),
    },
    location: {
      origin: "http://localhost:5173",
      replace() {},
    },
    fetch: async (url) => {
      const destino = new URL(url);
      requisicoes.push(destino.pathname + destino.search);
      if (destino.pathname === "/auth/me") {
        return resposta({ nome_usuario: "demo-classificados" });
      }
      if (destino.pathname === "/api/ads") {
        const status = destino.searchParams.get("status");
        const items = status === "published"
          ? [ad(1, "Anúncio publicado")]
          : [ad(2, "Anúncio expirado")];
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

  try {
    await import(`../js/paginas/meus_anuncios.js?teste=${Date.now()}`);

    assert.equal(elementos.get("#conteudo").hidden, false);
    assert.equal(elementos.get("#publicados").children.length, 1);
    assert.equal(elementos.get("#expirados").children.length, 1);
    assert.deepEqual(
      requisicoes.filter((url) => url.startsWith("/api/ads")),
      [
        "/api/ads?owner=me&status=published&page=1",
        "/api/ads?owner=me&status=expired&page=1",
      ],
    );
  } finally {
    for (const [nome, descritor] of anteriores) {
      if (descritor) Object.defineProperty(globalThis, nome, descritor);
      else delete globalThis[nome];
    }
  }
});
