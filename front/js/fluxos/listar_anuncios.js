import { MENSAGENS } from "../dominio/mensagens.js";
import { deveMostrarDestaques } from "../dominio/destaques.js";
import { parametrosDoFeed } from "../dominio/feed.js";
import { chamarApi, erroDoServidor } from "./conexao.js";
import { carregarUsuario } from "./sessao_atual.js";

export async function listarAnuncios(deps, parametros = new URLSearchParams()) {
  const usuario = await carregarUsuario(deps);
  if (usuario.tipo !== "logado") return usuario;

  const params = parametrosDoFeed(parametros);
  const { resposta, falha } = await chamarApi(() => deps.adsApi.listar({
    ...params,
    excluirEventos: deveMostrarDestaques(params),
  }));
  if (falha) return falha;

  if (resposta.status === 200) return { tipo: "feed", feed: resposta.corpo, params };
  if (resposta.status === 401) {
    deps.armazenamentoSessao.apagar();
    return { tipo: "sem_sessao", mensagem: MENSAGENS.sessaoExpirada };
  }
  return erroDoServidor(resposta);
}
