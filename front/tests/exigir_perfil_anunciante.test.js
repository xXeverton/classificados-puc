import test from "node:test";
import assert from "node:assert/strict";
import { exigirPerfilAnunciante } from "../js/fluxos/exigir_perfil_anunciante.js";
import {
  conexaoCaida,
  criarArmazenamentoFalso,
  criarAuthApiFalsa,
  criarPerfilApiFalso,
} from "./fakes.js";

const sessao = { token: "t", expira_em: "2030-01-01T00:00:00Z" };
const usuario = { nome: "Ana Souza", email: "ana@aluno.puc-rio.br", vinculo: "aluno" };
const anunciante = { nome_exibicao: "Ana Vende", foto_url: null, contatos: [] };

function montar({ me = { status: 200, corpo: usuario }, perfil, logado = true } = {}) {
  return {
    authApi: criarAuthApiFalsa({ me }),
    perfilApi: criarPerfilApiFalso({ obter: perfil }),
    armazenamentoSessao: criarArmazenamentoFalso(logado ? sessao : null),
  };
}

test("com perfil de anunciante, segue para a publicação (CA29)", async () => {
  const r = await exigirPerfilAnunciante(montar({ perfil: { status: 200, corpo: anunciante } }));
  assert.deepEqual(r, { tipo: "segue", usuario, anunciante });
});

test("sem perfil de anunciante (404), leva ao formulário com ?depois=anunciar (CA27)", async () => {
  const deps = montar({ perfil: { status: 404, corpo: { code: "perfil_nao_encontrado" } } });
  assert.deepEqual(await exigirPerfilAnunciante(deps), {
    tipo: "completar_perfil",
    destino: "/perfil/anunciante/?depois=anunciar",
  });
});

test("sem sessão leva à entrada sem consultar o perfil (CA30)", async () => {
  const deps = montar({ logado: false });
  const r = await exigirPerfilAnunciante(deps);
  assert.equal(r.tipo, "sem_sessao");
  assert.equal(deps.perfilApi.chamadas.length, 0);
});

test("401 do perfil de anunciante leva à entrada e apaga a sessão", async () => {
  const deps = montar({ perfil: { status: 401, corpo: {} } });
  const r = await exigirPerfilAnunciante(deps);
  assert.equal(r.tipo, "sem_sessao");
  assert.equal(deps.armazenamentoSessao.estado.sessao, null);
});

test("falhas de conexão e do servidor não liberam a publicação nem mandam ao formulário", async () => {
  assert.equal((await exigirPerfilAnunciante(montar({ perfil: conexaoCaida() }))).tipo, "conexao");
  const r = await exigirPerfilAnunciante(
    montar({ perfil: { status: 500, corpo: { message: "falhou" } } })
  );
  assert.deepEqual(r, { tipo: "erro_servidor", mensagem: "falhou" });
});
