import { chamarApi, erroDoServidor } from "./conexao.js";
import { carregarUsuario } from "./sessao_atual.js";

export async function detalharAnuncio(deps, id) {
  const usuario = await carregarUsuario(deps);
  if (usuario.tipo !== "logado") return usuario;

  const { resposta, falha } = await chamarApi(
    () => deps.adsApi.detalhar(id),
  );
  if (falha) return falha;

  if (resposta.status === 200) {
    return { tipo: "detalhes", detalhes: resposta.corpo };
  }
  if (resposta.status === 401) {
    deps.armazenamentoSessao.apagar();
    return {
      tipo: "sem_sessao",
      mensagem: "Faça login para ver os detalhes do anúncio.",
    };
  }
  return erroDoServidor(resposta);
}
