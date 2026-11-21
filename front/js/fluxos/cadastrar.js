import { validarCadastro } from "../dominio/regras_cadastro.js";
import { chamarApi, erroDoServidor } from "./conexao.js";

export async function cadastrar({ authApi }, dados) {
  const erros = validarCadastro(dados);
  if (Object.keys(erros).length > 0) return { tipo: "validacao", erros };

  const corpo = {
    nome: dados.nome.trim(),
    email: dados.email.trim(),
    nome_usuario: dados.nome_usuario.trim(),
    vinculo: dados.vinculo,
    senha: dados.senha,
  };
  const matricula = (dados.matricula ?? "").trim();
  if (matricula) corpo.matricula = matricula;

  const { resposta, falha } = await chamarApi(() => authApi.cadastrar(corpo));
  if (falha) return falha;

  if (resposta.status === 201) return { tipo: "verifique_email", email: corpo.email };
  return erroDoServidor(resposta);
}
