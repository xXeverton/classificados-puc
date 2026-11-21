import test from "node:test";
import assert from "node:assert/strict";
import { criarClienteHttp } from "../js/adaptadores/cliente_http.js";
import { ErroDeConexao } from "../js/dominio/erros.js";
import { criarFetchFalso } from "./fakes.js";

test("monta URL, envia JSON e devolve status e corpo", async () => {
  const { fetchFn, chamadas } = criarFetchFalso([{ status: 201, corpo: { id: 1 } }]);
  const cliente = criarClienteHttp({ fetchFn, baseUrl: "http://api" });
  const r = await cliente.requisitar("POST", "/auth/cadastro", { a: 1 });
  assert.deepEqual(r, { status: 201, corpo: { id: 1 } });
  assert.equal(chamadas[0].url, "http://api/auth/cadastro");
  assert.equal(chamadas[0].opcoes.body, '{"a":1}');
  assert.equal(chamadas[0].opcoes.headers.Authorization, undefined);
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
  assert.deepEqual(await cliente.requisitar("POST", "/auth/logout"), { status: 204, corpo: null });
});

test("rejeição do fetch vira ErroDeConexao", async () => {
  const { fetchFn } = criarFetchFalso([new TypeError("failed")]);
  const cliente = criarClienteHttp({ fetchFn, baseUrl: "http://api" });
  await assert.rejects(cliente.requisitar("GET", "/x"), ErroDeConexao);
});
