import test from "node:test";
import assert from "node:assert/strict";
import { confirmarEmail } from "../js/fluxos/confirmar_email.js";
import { criarAuthApiFalsa, conexaoCaida } from "./fakes.js";

test("sem token não chama a API", async () => {
  const authApi = criarAuthApiFalsa();
  for (const token of [null, ""]) {
    assert.equal((await confirmarEmail({ authApi }, token)).tipo, "sem_token");
  }
  assert.equal(authApi.chamadas.length, 0);
});

test("200, 410 e 400 viram confirmado, expirado e inválido", async () => {
  const casos = [[200, "confirmado"], [410, "expirado"], [400, "invalido"]];
  for (const [status, tipo] of casos) {
    const authApi = criarAuthApiFalsa({ confirmar: { status, corpo: {} } });
    assert.equal((await confirmarEmail({ authApi }, "abc")).tipo, tipo);
    assert.deepEqual(authApi.chamadas[0].args, ["abc"]);
  }
});

test("falha de conexão", async () => {
  const authApi = criarAuthApiFalsa({ confirmar: conexaoCaida() });
  assert.equal((await confirmarEmail({ authApi }, "abc")).tipo, "conexao");
});
