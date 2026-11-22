import { MENSAGENS } from "../dominio/mensagens.js";
import { chamarApi, erroDoServidor } from "./conexao.js";

export async function publicarAnuncio(deps, dados) {
  const { resposta, falha } = await chamarApi(
    () => deps.adsApi.publicar(dados),
  );
  if (falha) return falha;
  if (resposta.status === 201) {
    return { tipo: "publicado", anuncio: resposta.corpo };
  }
  if (resposta.status === 401) {
    deps.armazenamentoSessao.apagar();
    return { tipo: "sem_sessao", mensagem: MENSAGENS.sessaoExpirada };
  }
  if (
    resposta.status === 403
    && resposta.corpo?.code === "perfil_incompleto"
  ) {
    return {
      tipo: "completar_perfil",
      destino: "/perfil/anunciante/?depois=anunciar",
    };
  }
  if (resposta.corpo?.campos) {
    return {
      tipo: "dados_invalidos",
      campos: resposta.corpo.campos,
      mensagem: resposta.corpo.message,
    };
  }
  return erroDoServidor(resposta);
}
