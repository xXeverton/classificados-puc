import test from "node:test";
import assert from "node:assert/strict";
import {
  validarCadastro,
  validarLogin,
  validarEmailParaReenvio,
} from "../js/dominio/regras_cadastro.js";

const valido = () => ({
  nome: "Ana",
  email: "ana@aluno.puc-rio.br",
  nome_usuario: "ana",
  vinculo: "aluno",
  matricula: "",
  senha: "12345678",
  confirmacao_senha: "12345678",
});

test("login: campos vazios apontam cada campo", () => {
  const erros = validarLogin({ identificador: "  ", senha: "" });
  assert.deepEqual(Object.keys(erros).sort(), ["identificador", "senha"]);
});

test("login: preenchido não tem erros", () => {
  assert.deepEqual(validarLogin({ identificador: "ana", senha: "x" }), {});
});

test("cadastro válido não tem erros (matrícula vazia aceita)", () => {
  assert.deepEqual(validarCadastro(valido()), {});
});

test("cadastro: obrigatórios vazios", () => {
  const erros = validarCadastro({
    nome: "", email: "", nome_usuario: "", vinculo: "", senha: "",
    confirmacao_senha: "",
  });
  assert.deepEqual(Object.keys(erros).sort(), [
    "confirmacao_senha", "email", "nome", "nome_usuario", "senha", "vinculo",
  ]);
});

test("cadastro: domínio aceita os dois, ignora maiúsculas e espaços", () => {
  for (const email of [" ANA@PUC-RIO.BR ", "ana@aluno.puc-rio.br"]) {
    assert.equal(validarCadastro({ ...valido(), email }).email, undefined);
  }
});

test("cadastro: domínio não institucional é recusado", () => {
  for (const email of ["ana@gmail.com", "ana@puc-rio.br.com", "@puc-rio.br"]) {
    assert.ok(validarCadastro({ ...valido(), email }).email, email);
  }
});

test("cadastro: senha com 7 recusada e com 8 aceita", () => {
  const sete = { ...valido(), senha: "1234567", confirmacao_senha: "1234567" };
  assert.ok(validarCadastro(sete).senha);
  assert.equal(validarCadastro(valido()).senha, undefined);
});

test("cadastro: @ no nome de usuário", () => {
  assert.ok(validarCadastro({ ...valido(), nome_usuario: "a@na" }).nome_usuario);
});

test("cadastro: confirmação diferente da senha", () => {
  const erros = validarCadastro({ ...valido(), confirmacao_senha: "outra123" });
  assert.ok(erros.confirmacao_senha);
});

test("reenvio: e-mail vazio ou fora do domínio", () => {
  assert.ok(validarEmailParaReenvio(""));
  assert.ok(validarEmailParaReenvio("a@gmail.com"));
  assert.equal(validarEmailParaReenvio("a@puc-rio.br"), null);
});
