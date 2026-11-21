import { ErroDeConexao } from "../dominio/erros.js";
import { MENSAGENS } from "../dominio/mensagens.js";

// Executa uma chamada à API. Devolve { resposta } ou { falha: estado de tela }.
export async function chamarApi(chamada) {
  try {
    return { resposta: await chamada() };
  } catch (erro) {
    if (erro instanceof ErroDeConexao) {
      return { falha: { tipo: "conexao", mensagem: MENSAGENS.falhaDeConexao } };
    }
    throw erro;
  }
}

export function erroDoServidor(resposta) {
  return {
    tipo: "erro_servidor",
    mensagem: resposta.corpo?.message ?? MENSAGENS.erroInesperado,
  };
}
