import { MENSAGENS } from "../dominio/mensagens.js";
import { chamarApi, erroDoServidor } from "./conexao.js";

export async function confirmarEmail({ authApi }, token) {
  if (!token) return { tipo: "sem_token", mensagem: MENSAGENS.linkIncompleto };

  const { resposta, falha } = await chamarApi(() => authApi.confirmar(token));
  if (falha) return falha;

  if (resposta.status === 200) return { tipo: "confirmado" };
  if (resposta.status === 410) return { tipo: "expirado" };
  if (resposta.status === 400) return { tipo: "invalido" };
  return erroDoServidor(resposta);
}
