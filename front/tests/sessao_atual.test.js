import test from "node:test";
import assert from "node:assert/strict";
import { carregarUsuario, haSessao, sair } from "../js/fluxos/sessao_atual.js";
import { criarAuthApiFalsa, criarArmazenamentoFalso, conexaoCaida } from "./fakes.js";

const sessao = { token: "t", expira_em: "2030-01-01T00:00:00Z" };

test("haSessao reflete o armazenamento", () => {
  assert.equal(haSessao({ armazenamentoSessao: criarArmazenamentoFalso() }), false);
  assert.equal(haSessao({ armazenamentoSessao: criarArmazenamentoFalso(sessao) }), true);
});

test("nunca logou: pede ida à entrada sem aviso e sem chamar a API (CA20)", async () => {
  const authApi = criarAuthApiFalsa();
  const r = await carregarUsuario({ authApi, armazenamentoSessao: criarArmazenamentoFalso() });
  assert.deepEqual(r, { tipo: "sem_sessao", mensagem: null });
  assert.equal(authApi.chamadas.length, 0);
});

test("sessão vencida: pede ida à entrada com aviso (CA21)", async () => {
  const authApi = criarAuthApiFalsa();
  const armazenamentoSessao = criarArmazenamentoFalso(null, "expirada");
  const r = await carregarUsuario({ authApi, armazenamentoSessao });
  assert.equal(r.tipo, "sem_sessao");
  assert.ok(r.mensagem);
  assert.equal(authApi.chamadas.length, 0);
});

test("200 devolve o usuário", async () => {
  const usuario = { nome: "Ana" };
  const authApi = criarAuthApiFalsa({ me: { status: 200, corpo: usuario } });
  const r = await carregarUsuario({ authApi, armazenamentoSessao: criarArmazenamentoFalso(sessao) });
  assert.deepEqual(r, { tipo: "logado", usuario });
});

test("401 apaga a sessão e pede ida à entrada", async () => {
  const armazenamentoSessao = criarArmazenamentoFalso(sessao);
  const authApi = criarAuthApiFalsa({ me: { status: 401, corpo: {} } });
  const r = await carregarUsuario({ authApi, armazenamentoSessao });
  assert.equal(r.tipo, "sem_sessao");
  assert.equal(armazenamentoSessao.estado.sessao, null);
});

test("falha de conexão mantém a sessão", async () => {
  const armazenamentoSessao = criarArmazenamentoFalso(sessao);
  const authApi = criarAuthApiFalsa({ me: conexaoCaida() });
  assert.equal((await carregarUsuario({ authApi, armazenamentoSessao })).tipo, "conexao");
  assert.deepEqual(armazenamentoSessao.estado.sessao, sessao);
});

test("sair apaga a sessão com 204, 401 e sem conexão", async () => {
  for (const resposta of [{ status: 204, corpo: null }, { status: 401, corpo: {} }, conexaoCaida()]) {
    const armazenamentoSessao = criarArmazenamentoFalso(sessao);
    const authApi = criarAuthApiFalsa({ logout: resposta });
    const r = await sair({ authApi, armazenamentoSessao });
    assert.equal(r.tipo, "saiu");
    assert.equal(armazenamentoSessao.estado.sessao, null);
  }
});
