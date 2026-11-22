import test from "node:test";
import assert from "node:assert/strict";
import { contatoNovo, formularioInicial, obterPerfil } from "../js/fluxos/obter_perfil.js";
import {
  conexaoCaida,
  criarArmazenamentoFalso,
  criarAuthApiFalsa,
  criarPerfilApiFalso,
} from "./fakes.js";

const sessao = { token: "t", expira_em: "2030-01-01T00:00:00Z" };
const usuario = { nome: "Ana Souza", email: "ana@aluno.puc-rio.br", vinculo: "aluno" };
const anunciante = {
  nome_exibicao: "Ana Vende",
  foto_url: "/fotos-perfil/a.png",
  contatos: [
    { tipo: "link", codigo_pais: null, valor: "https://x.com/a", rotulo: "Loja", link_de_conversa: null },
    { tipo: "whatsapp", codigo_pais: "55", valor: "21999999999", rotulo: null, link_de_conversa: "https://wa.me/5521999999999" },
    { tipo: "email", codigo_pais: null, valor: "a@x.com", rotulo: null, link_de_conversa: null },
  ],
};

function montar({ me = { status: 200, corpo: usuario }, perfil, logado = true } = {}) {
  const authApi = criarAuthApiFalsa({ me });
  const perfilApi = criarPerfilApiFalso({ obter: perfil });
  const armazenamentoSessao = criarArmazenamentoFalso(logado ? sessao : null);
  return { authApi, perfilApi, armazenamentoSessao };
}

test("sem sessão: pede ida à entrada sem chamar a API (CA30)", async () => {
  const deps = montar({ logado: false });
  const r = await obterPerfil(deps);
  assert.equal(r.tipo, "sem_sessao");
  assert.equal(deps.perfilApi.chamadas.length, 0);
});

test("perfil comum de /auth/me e perfil de anunciante existente (CA1, CA3)", async () => {
  const deps = montar({ perfil: { status: 200, corpo: anunciante } });
  assert.deepEqual(await obterPerfil(deps), { tipo: "perfil", usuario, anunciante });
});

test("404 do anunciante: perfil comum sem anunciante (CA2)", async () => {
  const deps = montar({ perfil: { status: 404, corpo: { code: "perfil_nao_encontrado" } } });
  assert.deepEqual(await obterPerfil(deps), { tipo: "perfil", usuario, anunciante: null });
});

test("401 do /auth/me leva à entrada e apaga a sessão", async () => {
  const deps = montar({ me: { status: 401, corpo: {} } });
  const r = await obterPerfil(deps);
  assert.equal(r.tipo, "sem_sessao");
  assert.equal(deps.armazenamentoSessao.estado.sessao, null);
  assert.equal(deps.perfilApi.chamadas.length, 0);
});

test("401 do perfil de anunciante leva à entrada e apaga a sessão (CA30)", async () => {
  const deps = montar({ perfil: { status: 401, corpo: {} } });
  const r = await obterPerfil(deps);
  assert.equal(r.tipo, "sem_sessao");
  assert.ok(r.mensagem);
  assert.equal(deps.armazenamentoSessao.estado.sessao, null);
});

test("sem conexão e erro do servidor viram estados de tela", async () => {
  assert.equal((await obterPerfil(montar({ perfil: conexaoCaida() }))).tipo, "conexao");
  const r = await obterPerfil(montar({ perfil: { status: 500, corpo: { message: "falhou" } } }));
  assert.deepEqual(r, { tipo: "erro_servidor", mensagem: "falhou" });
  assert.equal((await obterPerfil(montar({ me: conexaoCaida() }))).tipo, "conexao");
});

test("formulário de quem não é anunciante: nome da conta e e-mail institucional (CA4)", () => {
  assert.deepEqual(formularioInicial({ usuario, anunciante: null }), {
    nome_exibicao: "Ana Souza",
    foto_url: null,
    contatos: [{ tipo: "email", codigo_pais: null, valor: "ana@aluno.puc-rio.br", rotulo: null }],
  });
});

test("formulário de quem já é anunciante: dados e ordem atuais, sem link_de_conversa (CA5)", () => {
  const f = formularioInicial({ usuario, anunciante });
  assert.equal(f.nome_exibicao, "Ana Vende");
  assert.equal(f.foto_url, "/fotos-perfil/a.png");
  assert.deepEqual(f.contatos.map((c) => c.tipo), ["link", "whatsapp", "email"]);
  assert.ok(f.contatos.every((c) => !("link_de_conversa" in c)));
});

test("contato novo: WhatsApp e telefone começam com Brasil; os demais sem país (CA12, CA14)", () => {
  assert.equal(contatoNovo("whatsapp").codigo_pais, "55");
  assert.equal(contatoNovo("telefone").codigo_pais, "55");
  for (const tipo of ["email", "site", "link"]) {
    assert.deepEqual(contatoNovo(tipo), { tipo, codigo_pais: null, valor: "", rotulo: null });
  }
});
