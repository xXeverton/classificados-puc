import { chamarApi } from "./conexao.js";

// A foto exige login (RN10), então um <img src> direto não funciona: baixamos
// com o token e entregamos um endereço blob:. Só um blob fica vivo por vez; o
// anterior é revogado ao trocar e ao sair da tela (`revogar`).
export function criarCarregadorDeFoto({ perfilApi, urlApi = URL }) {
  let atual = null;

  function revogar() {
    if (atual) urlApi.revokeObjectURL(atual);
    atual = null;
  }

  // Devolve o endereço blob: ou null (sem foto, 404, 401 ou sem conexão).
  async function carregar(fotoUrl) {
    revogar();
    if (!fotoUrl) return null;
    const { resposta, falha } = await chamarApi(() => perfilApi.foto(fotoUrl));
    if (falha || resposta.status !== 200 || !resposta.blob) return null;
    atual = urlApi.createObjectURL(resposta.blob);
    return atual;
  }

  return { carregar, revogar };
}
