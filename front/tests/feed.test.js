import test from "node:test";
import assert from "node:assert/strict";
import {
  contarFiltrosAtivos,
  dadosDoCard,
  lerFaixaDePreco,
  mensagemDeFeedVazio,
  montarParametrosFeed,
  montarUrlApi,
  paginasNumeradas,
  paramsSemFiltros,
  parametrosDoFeed,
  resumirDescricao,
} from "../js/dominio/feed.js";
import { listarAnuncios } from "../js/fluxos/listar_anuncios.js";
import {
  conexaoCaida,
  criarAdsApiFalsa,
  criarArmazenamentoFalso,
  criarAuthApiFalsa,
} from "./fakes.js";

const sessao = { token: "t", expira_em: "2030-01-01T00:00:00Z" };

test("dados do card incluem campos obrigatorios e foto opcional", () => {
  const card = dadosDoCard({
    id: 7,
    title: "Livro",
    description: null,
    type: "product",
    category: "Livros",
    price: 45,
    image_url: null,
    created_at: "2026-11-20T10:00:00Z",
  });
  assert.equal(card.titulo, "Livro");
  assert.equal(card.categoria, "Livros");
  assert.equal(card.preco, 45);
  assert.equal(card.imagem, null);
  assert.equal(card.detalhesUrl, "/anuncios/7/");
});

test("servico mostra descricao resumida e produto nao", () => {
  const texto = "a".repeat(121);
  assert.equal(resumirDescricao(texto).length, 120);
  const servico = dadosDoCard({
    id: 8,
    title: "Aulas",
    description: texto,
    type: "service",
    category: "Aulas",
    price: 30,
    image_url: "/foto.png",
    created_at: "2026-11-20T10:00:00Z",
  });
  assert.equal(servico.descricaoResumida.length, 120);
  assert.equal(servico.imagem, "/foto.png");
});

test("parametros padrao, validacao e URL da API", () => {
  assert.deepEqual(parametrosDoFeed(new URLSearchParams()), {
    page: 1,
    search: "",
    type: "all",
    minPrice: null,
    maxPrice: null,
  });
  assert.deepEqual(
    parametrosDoFeed(new URLSearchParams("page=3&search=livro&type=product")),
    { page: 3, search: "livro", type: "product", minPrice: null, maxPrice: null },
  );
  assert.deepEqual(
    parametrosDoFeed(new URLSearchParams("type=event")),
    { page: 1, search: "", type: "event", minPrice: null, maxPrice: null },
  );
  assert.equal(
    montarUrlApi({ page: 2, search: "cálculo", type: "product" }),
    "/api/ads?"+ "page=2&search=c%C3%A1lculo&type=product",
  );
  assert.equal(
    montarUrlApi({ page: 1, type: "event" }),
    "/api/ads?page=1&type=event",
  );
});

test("paginacao numerada retorna paginas da faixa atual", () => {
  assert.deepEqual(paginasNumeradas(1, 3), [1, 2, 3]);
  assert.deepEqual(paginasNumeradas(5, 10), [3, 4, 5, 6, 7]);
  assert.deepEqual(paginasNumeradas(10, 10), [6, 7, 8, 9, 10]);
  assert.deepEqual(paginasNumeradas(1, 0), []);
});

test("feed autenticado entrega dados e feed vazio", async () => {
  const feed = {
    items: [],
    page: 1,
    per_page: 20,
    total_pages: 0,
    total_items: 0,
    message: "Nenhum anúncio publicado encontrado.",
  };
  const deps = {
    authApi: criarAuthApiFalsa({ me: { status: 200, corpo: { nome: "Ana" } } }),
    adsApi: criarAdsApiFalsa({ listar: { status: 200, corpo: feed } }),
    armazenamentoSessao: criarArmazenamentoFalso(sessao),
  };
  const r = await listarAnuncios(deps, new URLSearchParams("page=1&type=all"));
  assert.equal(r.tipo, "feed");
  assert.deepEqual(r.feed, feed);
  assert.deepEqual(deps.adsApi.chamadas[0].args[0], {
    page: 1,
    search: "",
    type: "all",
    minPrice: null,
    maxPrice: null,
  });
});

test("feed sem sessao ou com falha nao chama listagem", async () => {
  const deps = {
    authApi: criarAuthApiFalsa(),
    adsApi: criarAdsApiFalsa(),
    armazenamentoSessao: criarArmazenamentoFalso(null),
  };
  assert.equal((await listarAnuncios(deps)).tipo, "sem_sessao");
  assert.equal(deps.adsApi.chamadas.length, 0);

  const offline = {
    authApi: criarAuthApiFalsa({ me: { status: 200, corpo: { nome: "Ana" } } }),
    adsApi: criarAdsApiFalsa({ listar: conexaoCaida() }),
    armazenamentoSessao: criarArmazenamentoFalso(sessao),
  };
  assert.equal((await listarAnuncios(offline)).tipo, "conexao");
});

test("faixa de preco vem da URL e ignora valores invalidos", () => {
  assert.deepEqual(
    parametrosDoFeed(new URLSearchParams("min_price=10&max_price=99.9")),
    { page: 1, search: "", type: "all", minPrice: 10, maxPrice: 99.9 },
  );
  for (const invalido of ["abc", "-1", "", "Infinity"]) {
    const params = parametrosDoFeed(
      new URLSearchParams({ min_price: invalido, max_price: invalido }),
    );
    assert.equal(params.minPrice, null, invalido);
    assert.equal(params.maxPrice, null, invalido);
  }
});

test("parametros do feed incluem faixa de preco so quando informada", () => {
  assert.equal(
    montarParametrosFeed({
      page: 2,
      search: "livro",
      type: "product",
      minPrice: 0,
      maxPrice: 50.5,
    }).toString(),
    "page=2&search=livro&type=product&min_price=0&max_price=50.5",
  );
  assert.equal(
    montarUrlApi({ page: 1, type: "all", minPrice: null, maxPrice: 80 }),
    "/api/ads?page=1&max_price=80",
  );
});

test("le a faixa de preco digitada com virgula ou ponto", () => {
  assert.deepEqual(lerFaixaDePreco("", ""), { minPrice: null, maxPrice: null });
  assert.deepEqual(lerFaixaDePreco(" 10,50 ", "200"), {
    minPrice: 10.5,
    maxPrice: 200,
  });
  assert.deepEqual(lerFaixaDePreco("30", "30.0"), {
    minPrice: 30,
    maxPrice: 30,
  });
});

test("recusa faixa de preco invalida com mensagem", () => {
  assert.deepEqual(lerFaixaDePreco("abc", ""), {
    erro: "Preço mínimo deve ser um número maior ou igual a zero.",
  });
  assert.deepEqual(lerFaixaDePreco("", "-5"), {
    erro: "Preço máximo deve ser um número maior ou igual a zero.",
  });
  assert.deepEqual(lerFaixaDePreco("1.000,00", ""), {
    erro: "Preço mínimo deve ser um número maior ou igual a zero.",
  });
  assert.deepEqual(lerFaixaDePreco("100", "50"), {
    erro: "Preço mínimo não pode ser maior que o máximo.",
  });
});

test("conta filtros ativos sem contar a busca", () => {
  const padrao = paramsSemFiltros();
  assert.equal(contarFiltrosAtivos(padrao), 0);
  assert.equal(contarFiltrosAtivos({ ...padrao, search: "livro" }), 0);
  assert.equal(contarFiltrosAtivos({ ...padrao, type: "service" }), 1);
  assert.equal(
    contarFiltrosAtivos({ ...padrao, type: "event", minPrice: 0, maxPrice: 10 }),
    3,
  );
});

test("limpar volta tudo ao padrao na primeira pagina", () => {
  assert.deepEqual(paramsSemFiltros(), {
    page: 1,
    search: "",
    type: "all",
    minPrice: null,
    maxPrice: null,
  });
});

test("feed vazio explica quando a busca ou os filtros nao acharam nada", () => {
  const padrao = paramsSemFiltros();
  const daApi = "Nenhum anúncio publicado encontrado.";
  assert.equal(mensagemDeFeedVazio(padrao, daApi), daApi);
  assert.equal(mensagemDeFeedVazio(padrao, undefined), daApi);
  for (const filtrado of [
    { ...padrao, search: "livro" },
    { ...padrao, type: "service" },
    { ...padrao, maxPrice: 10 },
  ]) {
    assert.equal(
      mensagemDeFeedVazio(filtrado, daApi),
      "Nenhum anúncio encontrado com esses filtros.",
    );
  }
});
