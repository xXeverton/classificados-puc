import { validarEmailParaReenvio } from "../dominio/regras_cadastro.js";
import { chamarApi, erroDoServidor } from "./conexao.js";

export async function reenviarConfirmacao({ authApi }, email) {
  const erro = validarEmailParaReenvio(email);
  if (erro) return { tipo: "validacao", erros: { email: erro } };

  const { resposta, falha } = await chamarApi(() => authApi.reenviar(email.trim()));
  if (falha) return falha;

  if (resposta.status === 202) {
    return { tipo: "reenviado", mensagem: resposta.corpo.message };
  }
  return erroDoServidor(resposta);
}
