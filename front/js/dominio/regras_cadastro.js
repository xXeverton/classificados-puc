import { MENSAGENS } from "./mensagens.js";

export const DOMINIOS_INSTITUCIONAIS = ["puc-rio.br", "aluno.puc-rio.br"];
export const TAMANHO_MINIMO_SENHA = 8;

const vazio = (valor) => !valor || valor.trim() === "";

export function emailInstitucional(email) {
  const normalizado = (email ?? "").trim().toLowerCase();
  return DOMINIOS_INSTITUCIONAIS.some((dominio) => {
    const sufixo = `@${dominio}`;
    return normalizado.endsWith(sufixo) && normalizado.length > sufixo.length;
  });
}

export function validarLogin({ identificador, senha }) {
  const erros = {};
  if (vazio(identificador)) erros.identificador = MENSAGENS.informeIdentificador;
  if (!senha) erros.senha = MENSAGENS.informeSenha;
  return erros;
}

export function validarEmailParaReenvio(email) {
  if (vazio(email)) return MENSAGENS.informeEmail;
  if (!emailInstitucional(email)) return MENSAGENS.emailNaoInstitucional;
  return null;
}

export function validarCadastro(dados) {
  const erros = {};
  for (const campo of ["nome", "email", "nome_usuario", "vinculo"]) {
    if (vazio(dados[campo])) erros[campo] = MENSAGENS.campoObrigatorio;
  }
  if (!erros.email && !emailInstitucional(dados.email)) {
    erros.email = MENSAGENS.emailNaoInstitucional;
  }
  if (!erros.nome_usuario && dados.nome_usuario.includes("@")) {
    erros.nome_usuario = MENSAGENS.nomeUsuarioComArroba;
  }
  if (!dados.senha) {
    erros.senha = MENSAGENS.campoObrigatorio;
  } else if (dados.senha.length < TAMANHO_MINIMO_SENHA) {
    erros.senha = MENSAGENS.senhaCurta;
  }
  if (!dados.confirmacao_senha) {
    erros.confirmacao_senha = MENSAGENS.campoObrigatorio;
  } else if (dados.confirmacao_senha !== dados.senha) {
    erros.confirmacao_senha = MENSAGENS.senhasDiferentes;
  }
  return erros;
}
