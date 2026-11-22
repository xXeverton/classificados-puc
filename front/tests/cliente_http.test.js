import test from "node:test";
import assert from "node:assert/strict";
import { criarClienteHttp } from "../js/adaptadores/cliente_http.js";
import { ErroDeConexao } from "../js/dominio/erros.js";
import { criarFetchFalso } from "./fakes.js";

test("monta URL, envia JSON e devolve status e corpo", async () => {
  const { fetchFn, chamadas } = criarFetchFalso([{ status: 201, corpo: { id: 1 } }]);
  const cliente = criarClienteHttp({ fetchFn, baseUrl: "http://api" });
  const r = await cliente.requisitar("POST", "/auth/cadastro", { a: 1 });
  assert.deepEqual(r, {
    status: 201,
    corpo: { id: 1 },
    redirecionada: false,
  });
  assert.equal(chamadas[0].url, "http://api/auth/cadastro");
  assert.equal(chamadas[0].opcoes.body, '{"a":1}');
  assert.equal(chamadas[0].opcoes.headers.Authorization, undefined);
  assert.equal(chamadas[0].opcoes.credentials, "same-origin");
});

test("envia Bearer quando há token", async () => {
  const { fetchFn, chamadas } = criarFetchFalso();
  const cliente = criarClienteHttp({ fetchFn, baseUrl: "http://api", obterToken: () => "t0k" });
  await cliente.requisitar("GET", "/auth/me");
  assert.equal(chamadas[0].opcoes.headers.Authorization, "Bearer t0k");
  assert.equal(chamadas[0].opcoes.body, undefined);
});

test("corpo ausente vira null", async () => {
  const { fetchFn } = criarFetchFalso([{ status: 204 }]);
  const cliente = criarClienteHttp({ fetchFn, baseUrl: "http://api" });
  assert.deepEqual(await cliente.requisitar("POST", "/auth/logout"), {
    status: 204,
    corpo: null,
    redirecionada: false,
  });
});

test("FormData vai como está, sem Content-Type (o navegador define o boundary)", async () => {
  const { fetchFn, chamadas } = criarFetchFalso();
  const cliente = criarClienteHttp({ fetchFn, baseUrl: "http://api", obterToken: () => "t0k" });
  const formulario = new FormData();
  formulario.append("nome_exibicao", "Ana");
  await cliente.requisitar("PUT", "/perfil-anunciante", formulario);
  assert.equal(chamadas[0].opcoes.body, formulario);
  assert.equal(chamadas[0].opcoes.headers["Content-Type"], undefined);
  assert.equal(chamadas[0].opcoes.headers.Authorization, "Bearer t0k");
});

test("baixar envia o token e devolve o blob só com 200", async () => {
  const blob = new Blob(["x"], { type: "image/png" });
  const chamadas = [];
  const respostas = [{ status: 200, blob: async () => blob }, { status: 404 }];
  const fetchFn = async (url, opcoes) => {
    chamadas.push({ url, opcoes });
    return respostas.shift();
  };
  const cliente = criarClienteHttp({ fetchFn, baseUrl: "http://api", obterToken: () => "t0k" });
  assert.deepEqual(await cliente.baixar("/fotos-perfil/a.png"), { status: 200, blob });
  assert.equal(chamadas[0].url, "http://api/fotos-perfil/a.png");
  assert.equal(chamadas[0].opcoes.headers.Authorization, "Bearer t0k");
  assert.deepEqual(await cliente.baixar("/fotos-perfil/b.png"), { status: 404, blob: null });
});

test("baixar: rejeição do fetch vira ErroDeConexao", async () => {
  const cliente = criarClienteHttp({
    fetchFn: async () => { throw new TypeError("failed"); },
    baseUrl: "http://api",
  });
  await assert.rejects(cliente.baixar("/fotos-perfil/a.png"), ErroDeConexao);
});

test("rejeição do fetch vira ErroDeConexao", async () => {
  const { fetchFn } = criarFetchFalso([new TypeError("failed")]);
  const cliente = criarClienteHttp({ fetchFn, baseUrl: "http://api" });
  await assert.rejects(cliente.requisitar("GET", "/x"), ErroDeConexao);
});
