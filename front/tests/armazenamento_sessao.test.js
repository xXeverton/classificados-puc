import test from "node:test";
import assert from "node:assert/strict";
import { criarArmazenamentoSessao, CHAVE_SESSAO } from "../js/adaptadores/armazenamento_sessao.js";
import { criarStorageEmMemoria } from "./fakes.js";

const AGORA = Date.parse("2026-01-01T12:00:00Z");

test("salva e lê sessão válida", () => {
  const arm = criarArmazenamentoSessao(criarStorageEmMemoria(), () => AGORA);
  const sessao = { token: "t", expira_em: "2026-01-01T20:00:00Z" };
  arm.salvar(sessao);
  assert.deepEqual(arm.ler(), sessao);
});

test("sessão vencida é ausente e apagada", () => {
  const storage = criarStorageEmMemoria();
  const arm = criarArmazenamentoSessao(storage, () => AGORA);
  arm.salvar({ token: "t", expira_em: "2026-01-01T11:00:00Z" });
  assert.equal(arm.ler(), null);
  assert.equal(storage.getItem(CHAVE_SESSAO), null);
});

test("lerComMotivo distingue ausente de expirada", () => {
  const arm = criarArmazenamentoSessao(criarStorageEmMemoria(), () => AGORA);
  assert.deepEqual(arm.lerComMotivo(), { sessao: null, motivo: "ausente" });
  arm.salvar({ token: "t", expira_em: "2026-01-01T11:00:00Z" });
  assert.deepEqual(arm.lerComMotivo(), { sessao: null, motivo: "expirada" });
  assert.deepEqual(arm.lerComMotivo(), { sessao: null, motivo: "ausente" });
});

test("apagar remove; conteúdo corrompido é ausente", () => {
  const storage = criarStorageEmMemoria();
  const arm = criarArmazenamentoSessao(storage, () => AGORA);
  storage.setItem(CHAVE_SESSAO, "{ruim");
  assert.equal(arm.ler(), null);
  arm.salvar({ token: "t", expira_em: "2026-01-01T20:00:00Z" });
  arm.apagar();
  assert.equal(arm.ler(), null);
});
