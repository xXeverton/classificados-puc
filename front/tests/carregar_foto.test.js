import test from "node:test";
import assert from "node:assert/strict";
import { criarCarregadorDeFoto } from "../js/fluxos/carregar_foto.js";
import { conexaoCaida, criarPerfilApiFalso } from "./fakes.js";

function urlFalsa() {
  const criados = [];
  const revogados = [];
  return {
    criados,
    revogados,
    createObjectURL: (blob) => {
      criados.push(blob);
      return `blob:${criados.length}`;
    },
    revokeObjectURL: (url) => revogados.push(url),
  };
}

const blob = new Blob(["x"], { type: "image/png" });
const ok = { status: 200, blob };

test("baixa a foto pelo caminho do perfil e devolve um blob:", async () => {
  const perfilApi = criarPerfilApiFalso({ foto: ok });
  const urlApi = urlFalsa();
  const carregador = criarCarregadorDeFoto({ perfilApi, urlApi });
  assert.equal(await carregador.carregar("/fotos-perfil/a.png"), "blob:1");
  assert.deepEqual(perfilApi.chamadas[0], { nome: "foto", args: ["/fotos-perfil/a.png"] });
  assert.deepEqual(urlApi.criados, [blob]);
});

test("sem foto não chama a API", async () => {
  const perfilApi = criarPerfilApiFalso({ foto: ok });
  const carregador = criarCarregadorDeFoto({ perfilApi, urlApi: urlFalsa() });
  assert.equal(await carregador.carregar(null), null);
  assert.equal(perfilApi.chamadas.length, 0);
});

test("o blob: anterior é revogado ao carregar outra foto e ao sair", async () => {
  const urlApi = urlFalsa();
  const carregador = criarCarregadorDeFoto({ perfilApi: criarPerfilApiFalso({ foto: ok }), urlApi });
  await carregador.carregar("/fotos-perfil/a.png");
  await carregador.carregar("/fotos-perfil/b.png");
  assert.deepEqual(urlApi.revogados, ["blob:1"]);
  carregador.revogar();
  carregador.revogar();
  assert.deepEqual(urlApi.revogados, ["blob:1", "blob:2"]);
});

test("404, 401 e falta de conexão devolvem null, sem criar blob:", async () => {
  for (const resposta of [{ status: 404, blob: null }, { status: 401, blob: null }, conexaoCaida()]) {
    const urlApi = urlFalsa();
    const carregador = criarCarregadorDeFoto({ perfilApi: criarPerfilApiFalso({ foto: resposta }), urlApi });
    assert.equal(await carregador.carregar("/fotos-perfil/a.png"), null);
    assert.equal(urlApi.criados.length, 0);
  }
});
