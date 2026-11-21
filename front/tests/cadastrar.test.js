import test from "node:test";
import assert from "node:assert/strict";
import { cadastrar } from "../js/fluxos/cadastrar.js";
import { criarAuthApiFalsa, conexaoCaida } from "./fakes.js";

const valido = () => ({
  nome: " Ana ",
  email: " ana@aluno.puc-rio.br ",
  nome_usuario: "ana",
  vinculo: "aluno",
  matricula: "",
  senha: "12345678",
  confirmacao_senha: "12345678",
});

test("dados inválidos não chamam a API", async () => {
  const authApi = criarAuthApiFalsa();
  const r = await cadastrar({ authApi }, { ...valido(), email: "a@gmail.com" });
  assert.equal(r.tipo, "validacao");
  assert.ok(r.erros.email);
  assert.equal(authApi.chamadas.length, 0);
});

test("201 vira verifique_email com o endereço; confirmação e matrícula vazia não vão no corpo", async () => {
  const authApi = criarAuthApiFalsa({ cadastrar: { status: 201, corpo: {} } });
  const r = await cadastrar({ authApi }, valido());
  assert.deepEqual(r, { tipo: "verifique_email", email: "ana@aluno.puc-rio.br" });
  const corpo = authApi.chamadas[0].args[0];
  assert.deepEqual(corpo, {
    nome: "Ana",
    email: "ana@aluno.puc-rio.br",
    nome_usuario: "ana",
    vinculo: "aluno",
    senha: "12345678",
  });
});

test("matrícula preenchida é enviada", async () => {
  const authApi = criarAuthApiFalsa({ cadastrar: { status: 201, corpo: {} } });
  await cadastrar({ authApi }, { ...valido(), matricula: "123" });
  assert.equal(authApi.chamadas[0].args[0].matricula, "123");
});

test("409 e 400 trazem a mensagem do servidor", async () => {
  for (const status of [409, 400]) {
    const authApi = criarAuthApiFalsa({ cadastrar: { status, corpo: { message: "E-mail já em uso" } } });
    const r = await cadastrar({ authApi }, valido());
    assert.deepEqual(r, { tipo: "erro_servidor", mensagem: "E-mail já em uso" });
  }
});

test("falha de conexão", async () => {
  const authApi = criarAuthApiFalsa({ cadastrar: conexaoCaida() });
  assert.equal((await cadastrar({ authApi }, valido())).tipo, "conexao");
});
