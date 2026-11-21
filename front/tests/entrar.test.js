import test from "node:test";
import assert from "node:assert/strict";
import { entrar } from "../js/fluxos/entrar.js";
import { criarAuthApiFalsa, criarArmazenamentoFalso, conexaoCaida } from "./fakes.js";

const dados = { identificador: " ana ", senha: "12345678" };

function montar(respostas) {
  const authApi = criarAuthApiFalsa(respostas);
  const armazenamentoSessao = criarArmazenamentoFalso();
  return { authApi, armazenamentoSessao, deps: { authApi, armazenamentoSessao } };
}

test("campos vazios não chamam a API", async () => {
  const { authApi, deps } = montar();
  const r = await entrar(deps, { identificador: "", senha: "" });
  assert.equal(r.tipo, "validacao");
  assert.deepEqual(Object.keys(r.erros).sort(), ["identificador", "senha"]);
  assert.equal(authApi.chamadas.length, 0);
});

test("200 salva a sessão e devolve sucesso", async () => {
  const sessao = { token: "t", expira_em: "2030-01-01T00:00:00Z" };
  const { authApi, armazenamentoSessao, deps } = montar({ login: { status: 200, corpo: sessao } });
  const r = await entrar(deps, dados);
  assert.equal(r.tipo, "sucesso");
  assert.deepEqual(armazenamentoSessao.estado.salvos, [sessao]);
  assert.deepEqual(authApi.chamadas[0].args, ["ana", "12345678"]);
});

test("401 vira credenciais inválidas sem salvar sessão", async () => {
  const { armazenamentoSessao, deps } = montar({ login: { status: 401, corpo: { message: "x" } } });
  const r = await entrar(deps, dados);
  assert.equal(r.tipo, "credenciais_invalidas");
  assert.equal(r.mensagem, "Credenciais inválidas.");
  assert.equal(armazenamentoSessao.estado.salvos.length, 0);
});

test("403 email_nao_confirmado", async () => {
  const { deps } = montar({ login: { status: 403, corpo: { message: "m", code: "email_nao_confirmado" } } });
  assert.equal((await entrar(deps, dados)).tipo, "email_nao_confirmado");
});

test("403 sem o código vira erro do servidor", async () => {
  const { deps } = montar({ login: { status: 403, corpo: { message: "Proibido" } } });
  const r = await entrar(deps, dados);
  assert.deepEqual(r, { tipo: "erro_servidor", mensagem: "Proibido" });
});

test("429 vira bloqueado", async () => {
  const { deps } = montar({ login: { status: 429, corpo: { message: "m" } } });
  assert.equal((await entrar(deps, dados)).tipo, "bloqueado");
});

test("400 mostra a mensagem do servidor", async () => {
  const { deps } = montar({ login: { status: 400, corpo: { message: "Dados inválidos" } } });
  assert.deepEqual(await entrar(deps, dados), { tipo: "erro_servidor", mensagem: "Dados inválidos" });
});

test("falha de conexão vira estado de conexão", async () => {
  const { deps } = montar({ login: conexaoCaida() });
  assert.equal((await entrar(deps, dados)).tipo, "conexao");
});
