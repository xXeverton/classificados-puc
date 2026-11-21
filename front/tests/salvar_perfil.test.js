import test from "node:test";
import assert from "node:assert/strict";
import { destinoAposSalvar, salvarPerfil } from "../js/fluxos/salvar_perfil.js";
import { MENSAGENS } from "../js/dominio/mensagens.js";
import { conexaoCaida, criarArmazenamentoFalso, criarPerfilApiFalso } from "./fakes.js";

const sessao = { token: "t", expira_em: "2030-01-01T00:00:00Z" };
const email = { tipo: "email", codigo_pais: null, valor: " Ana@X.com ", rotulo: null };
const zap = { tipo: "whatsapp", codigo_pais: "55", valor: "(21) 99999-9999", rotulo: null };
const dados = (extra = {}) => ({
  nome_exibicao: "  Ana Vende ",
  contatos: [zap, email],
  foto: null,
  remover_foto: false,
  ...extra,
});

function montar(salvar) {
  const perfilApi = criarPerfilApiFalso({ salvar });
  const armazenamentoSessao = criarArmazenamentoFalso(sessao);
  return { perfilApi, armazenamentoSessao, deps: { perfilApi, armazenamentoSessao } };
}

test("dados inválidos não chamam a API (CA7, CA8)", async () => {
  const { perfilApi, deps } = montar();
  const r = await salvarPerfil(deps, dados({ nome_exibicao: " ", contatos: [] }));
  assert.equal(r.tipo, "validacao");
  assert.ok(r.erros.campos.nome_exibicao);
  assert.ok(r.erros.campos.contatos);
  assert.equal(perfilApi.chamadas.length, 0);
});

test("monta o multipart com nome, contatos normalizados em JSON e ordem preservada (CA19)", async () => {
  const { perfilApi, deps } = montar({ status: 200, corpo: { nome_exibicao: "Ana Vende" } });
  await salvarPerfil(deps, dados());
  const formulario = perfilApi.chamadas[0].args[0];
  assert.ok(formulario instanceof FormData);
  assert.equal(formulario.get("nome_exibicao"), "Ana Vende");
  assert.deepEqual(JSON.parse(formulario.get("contatos")), [
    { tipo: "whatsapp", codigo_pais: "55", valor: "21999999999", rotulo: null },
    { tipo: "email", codigo_pais: null, valor: "ana@x.com", rotulo: null },
  ]);
  assert.equal(formulario.get("foto"), null);
  assert.equal(formulario.get("remover_foto"), null);
});

test("envia a foto escolhida (CA23)", async () => {
  const { perfilApi, deps } = montar({ status: 200, corpo: {} });
  const foto = new Blob(["abc"], { type: "image/png" });
  await salvarPerfil(deps, dados({ foto }));
  const enviada = perfilApi.chamadas[0].args[0].get("foto");
  assert.equal(enviada.size, 3);
});

test("remover foto sem foto nova envia remover_foto (CA26)", async () => {
  const { perfilApi, deps } = montar({ status: 200, corpo: {} });
  await salvarPerfil(deps, dados({ remover_foto: true }));
  assert.equal(perfilApi.chamadas[0].args[0].get("remover_foto"), "true");
});

test("com foto nova, remover_foto não é enviado", async () => {
  const { perfilApi, deps } = montar({ status: 200, corpo: {} });
  const foto = new Blob(["abc"], { type: "image/png" });
  await salvarPerfil(deps, dados({ foto, remover_foto: true }));
  assert.equal(perfilApi.chamadas[0].args[0].get("remover_foto"), null);
});

test("200 devolve sucesso e o destino padrão (CA6, CA9)", async () => {
  const corpo = { nome_exibicao: "Ana Vende" };
  const { deps } = montar({ status: 200, corpo });
  assert.deepEqual(await salvarPerfil(deps, dados()), {
    tipo: "sucesso",
    anunciante: corpo,
    destino: "/perfil/",
  });
});

test("?depois=anunciar volta à publicação (CA28); valores fora da lista são ignorados", async () => {
  assert.equal(destinoAposSalvar("anunciar"), "/anuncios/novo/");
  for (const depois of [undefined, null, "", "https://evil.com", "//evil.com", "__proto__", "constructor", "toString"]) {
    assert.equal(destinoAposSalvar(depois), "/perfil/", String(depois));
  }
  const { deps } = montar({ status: 200, corpo: {} });
  assert.equal((await salvarPerfil(deps, dados(), "anunciar")).destino, "/anuncios/novo/");
  assert.equal((await salvarPerfil(deps, dados(), "https://evil.com")).destino, "/perfil/");
});

test("400 mostra o motivo; foto_invalida aponta o campo da foto (CA24)", async () => {
  const dadosInvalidos = montar({ status: 400, corpo: { message: "Contato 2 inválido", code: "dados_invalidos" } });
  assert.deepEqual(await salvarPerfil(dadosInvalidos.deps, dados()), {
    tipo: "dados_invalidos",
    mensagem: "Contato 2 inválido",
    campo: null,
  });
  const foto = montar({ status: 400, corpo: { message: "Formato inválido", code: "foto_invalida" } });
  assert.equal((await salvarPerfil(foto.deps, dados())).campo, "foto");
});

test("413 vira arquivo_grande", async () => {
  const { deps } = montar({ status: 413, corpo: { message: "grande demais", code: "arquivo_grande" } });
  assert.deepEqual(await salvarPerfil(deps, dados()), { tipo: "arquivo_grande", mensagem: "grande demais" });
  const semCorpo = montar({ status: 413, corpo: null });
  assert.equal((await salvarPerfil(semCorpo.deps, dados())).mensagem, MENSAGENS.fotoGrande);
});

test("401 apaga a sessão e leva à entrada (CA30)", async () => {
  const { armazenamentoSessao, deps } = montar({ status: 401, corpo: {} });
  const r = await salvarPerfil(deps, dados());
  assert.equal(r.tipo, "sem_sessao");
  assert.equal(armazenamentoSessao.estado.sessao, null);
});

test("sem conexão e erro do servidor preservam a sessão", async () => {
  const semConexao = montar(conexaoCaida());
  assert.equal((await salvarPerfil(semConexao.deps, dados())).tipo, "conexao");
  assert.deepEqual(semConexao.armazenamentoSessao.estado.sessao, sessao);
  const erro = montar({ status: 500, corpo: null });
  assert.equal((await salvarPerfil(erro.deps, dados())).tipo, "erro_servidor");
});
