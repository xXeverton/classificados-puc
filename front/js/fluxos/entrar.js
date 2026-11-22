import { validarLogin } from "../dominio/regras_cadastro.js";
import { MENSAGENS } from "../dominio/mensagens.js";
import { chamarApi, erroDoServidor } from "./conexao.js";

export async function entrar({ authApi, armazenamentoSessao }, dados) {
  const erros = validarLogin(dados);
  if (Object.keys(erros).length > 0) return { tipo: "validacao", erros };

  const { resposta, falha } = await chamarApi(() =>
    authApi.login(dados.identificador.trim(), dados.senha)
  );
  if (falha) return falha;

  if (resposta.status === 200) {
    armazenamentoSessao.salvar(resposta.corpo);
    return { tipo: "sucesso" };
  }
  if (resposta.status === 401) {
    return { tipo: "credenciais_invalidas", mensagem: MENSAGENS.credenciaisInvalidas };
  }
  if (resposta.status === 403 && resposta.corpo?.code === "email_nao_confirmado") {
    return { tipo: "email_nao_confirmado", mensagem: MENSAGENS.emailNaoConfirmado };
  }
  if (resposta.status === 429) {
    return { tipo: "bloqueado", mensagem: MENSAGENS.contaBloqueada };
  }
  return erroDoServidor(resposta);
}
