import { MENSAGENS } from "../dominio/mensagens.js";
import { mapearErrosPublicacao } from "../dominio/anuncio.js";
import { chamarApi } from "./conexao.js";

export async function publicarAnuncio(deps, dados) {
  const { resposta, falha } = await chamarApi(
    () => deps.adsApi.publicar(dados),
  );
  if (falha) {
    return {
      tipo: "conexao",
      mensagem: MENSAGENS.publicacaoSemConexao,
    };
  }
  if (resposta.redirecionada || resposta.status === 401) {
    deps.armazenamentoSessao.apagar();
    return { tipo: "sem_sessao", mensagem: MENSAGENS.sessaoExpirada };
  }
  if (resposta.status === 201) {
    return { tipo: "publicado", anuncio: resposta.corpo };
  }
  if (
    resposta.status === 403
    && resposta.corpo?.code === "perfil_incompleto"
  ) {
    return {
      tipo: "perfil_incompleto",
      mensagem: MENSAGENS.perfilIncompletoParaAnunciar,
    };
  }
  if (resposta.status === 413) {
    return {
      tipo: "dados_invalidos",
      campos: { imagem: MENSAGENS.fotoGrande },
    };
  }
  if (
    resposta.status === 400
    && resposta.corpo?.code === "imagem_invalida"
  ) {
    return {
      tipo: "dados_invalidos",
      campos: { imagem: resposta.corpo.message ?? MENSAGENS.fotoFormato },
    };
  }
  if (
    [400, 422].includes(resposta.status)
    && resposta.corpo?.campos
    && typeof resposta.corpo.campos === "object"
    && !Array.isArray(resposta.corpo.campos)
  ) {
    const mapeamento = mapearErrosPublicacao(resposta.corpo.campos);
    return {
      tipo: "dados_invalidos",
      campos: mapeamento.erros,
      temCampoDesconhecido: mapeamento.temCampoDesconhecido,
      mensagem: resposta.corpo.message,
    };
  }
  return {
    tipo: "erro_servidor",
    mensagem: MENSAGENS.publicacaoFalhou,
  };
}
