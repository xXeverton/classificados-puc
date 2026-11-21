import test from "node:test";
import assert from "node:assert/strict";
import { reenviarConfirmacao } from "../js/fluxos/reenviar_confirmacao.js";
import { criarAuthApiFalsa, conexaoCaida } from "./fakes.js";

test("e-mail vazio ou fora do domínio não chama a API", async () => {
  const authApi = criarAuthApiFalsa();
  for (const email of ["", "a@gmail.com"]) {
    const r = await reenviarConfirmacao({ authApi }, email);
    assert.equal(r.tipo, "validacao");
    assert.ok(r.erros.email);
  }
  assert.equal(authApi.chamadas.length, 0);
});

test("202 devolve a mensagem genérica do servidor", async () => {
  const authApi = criarAuthApiFalsa({ reenviar: { status: 202, corpo: { message: "Se houver..." } } });
  const r = await reenviarConfirmacao({ authApi }, " a@puc-rio.br ");
  assert.deepEqual(r, { tipo: "reenviado", mensagem: "Se houver..." });
  assert.deepEqual(authApi.chamadas[0].args, ["a@puc-rio.br"]);
});

test("falha de conexão", async () => {
  const authApi = criarAuthApiFalsa({ reenviar: conexaoCaida() });
  assert.equal((await reenviarConfirmacao({ authApi }, "a@puc-rio.br")).tipo, "conexao");
});
