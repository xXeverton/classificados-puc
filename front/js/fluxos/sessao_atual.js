import { MENSAGENS } from "../dominio/mensagens.js";
import { chamarApi, erroDoServidor } from "./conexao.js";

export function haSessao({ armazenamentoSessao }) {
  return armazenamentoSessao.ler() !== null;
}

export async function carregarUsuario({ authApi, armazenamentoSessao }) {
  const { sessao, motivo } = armazenamentoSessao.lerComMotivo();
  if (!sessao) {
    // Só avisa quando havia sessão e ela venceu (CA21); quem nunca entrou não (CA20).
    return {
      tipo: "sem_sessao",
      mensagem: motivo === "expirada" ? MENSAGENS.sessaoExpirada : null,
    };
  }
  const { resposta, falha } = await chamarApi(() => authApi.me());
  if (falha) return falha;

  if (resposta.status === 200) return { tipo: "logado", usuario: resposta.corpo };
  if (resposta.status === 401) {
    armazenamentoSessao.apagar();
    return { tipo: "sem_sessao", mensagem: MENSAGENS.sessaoExpirada };
  }
  return erroDoServidor(resposta);
}

// A pessoa sempre sai neste navegador, mesmo que o servidor não responda.
export async function sair({ authApi, armazenamentoSessao }) {
  try {
    await chamarApi(() => authApi.logout());
  } finally {
    armazenamentoSessao.apagar();
  }
  return { tipo: "saiu" };
}
