import test from "node:test";
import assert from "node:assert/strict";
import { ErroDeConexao } from "../js/dominio/erros.js";
import { publicarAnuncio } from "../js/fluxos/publicar_anuncio.js";

function montar(resposta) {
  const armazenamentoSessao = {
    apagado: 0,
    apagar() {
      this.apagado += 1;
    },
  };
  return {
    armazenamentoSessao,
    deps: {
      armazenamentoSessao,
      adsApi: {
        publicar: async () => {
          if (resposta instanceof Error) throw resposta;
          return resposta;
        },
      },
    },
  };
}

test("201 confirma publicação", async () => {
  const { deps } = montar({ status: 201, corpo: { id: 7 } });
  assert.deepEqual(await publicarAnuncio(deps, new FormData()), {
    tipo: "publicado",
    anuncio: { id: 7 },
  });
});

test("401 ou redirecionamento apagam a sessão", async () => {
  for (const resposta of [
    { status: 401, corpo: {} },
    { status: 200, corpo: {}, redirecionada: true },
  ]) {
    const { deps, armazenamentoSessao } = montar(resposta);
    assert.equal((await publicarAnuncio(deps, new FormData())).tipo, "sem_sessao");
    assert.equal(armazenamentoSessao.apagado, 1);
  }
});

test("403 de perfil incompleto preserva formulário e sessão", async () => {
  const { deps, armazenamentoSessao } = montar({
    status: 403,
    corpo: { code: "perfil_incompleto" },
  });
  assert.equal(
    (await publicarAnuncio(deps, new FormData())).tipo,
    "perfil_incompleto",
  );
  assert.equal(armazenamentoSessao.apagado, 0);
});

test("mapeia erros conhecidos para campos e sinaliza os desconhecidos", async () => {
  const { deps: depsConhecidos } = montar({
    status: 422,
    corpo: {
      message: "Inválido",
      campos: { preco_a_combinar: "Escolha uma opção." },
    },
  });
  assert.deepEqual(
    await publicarAnuncio(depsConhecidos, new FormData()),
    {
      tipo: "dados_invalidos",
      campos: { tipo_preco: "Escolha uma opção." },
      temCampoDesconhecido: false,
      mensagem: "Inválido",
    },
  );

  const { deps: depsDesconhecidos } = montar({
    status: 422,
    corpo: { campos: { admin: "Não permitido." } },
  });
  const estado = await publicarAnuncio(depsDesconhecidos, new FormData());
  assert.deepEqual(estado.campos, {});
  assert.equal(estado.temCampoDesconhecido, true);
});

test("falhas de conexão e servidor retornam mensagens sem apagar sessão", async () => {
  const { deps: depsConexao, armazenamentoSessao: sessaoConexao } =
    montar(new ErroDeConexao(new Error("offline")));
  assert.equal(
    (await publicarAnuncio(depsConexao, new FormData())).tipo,
    "conexao",
  );
  assert.equal(sessaoConexao.apagado, 0);

  const { deps: depsServidor } = montar({ status: 500, corpo: null });
  assert.equal(
    (await publicarAnuncio(depsServidor, new FormData())).tipo,
    "erro_servidor",
  );
});
