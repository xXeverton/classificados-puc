import { ErroDeConexao } from "../dominio/erros.js";

export function criarClienteHttp({ fetchFn, baseUrl, obterToken = () => null }) {
  async function requisitar(metodo, caminho, corpo) {
    const cabecalhos = { Accept: "application/json" };
    const opcoes = {
      method: metodo,
      headers: cabecalhos,
      credentials: "same-origin",
    };
    if (corpo instanceof FormData) {
      // O navegador define o Content-Type do multipart, com o boundary.
      opcoes.body = corpo;
    } else if (corpo !== undefined) {
      cabecalhos["Content-Type"] = "application/json";
      opcoes.body = JSON.stringify(corpo);
    }
    const resposta = await enviar(caminho, opcoes, cabecalhos);
    return {
      status: resposta.status,
      corpo: await lerCorpo(resposta),
      redirecionada: resposta.redirected === true,
    };
  }

  // Arquivos (fotos): devolve o conteúdo só quando a resposta é 200.
  async function baixar(caminho) {
    const cabecalhos = {};
    const resposta = await enviar(caminho, { method: "GET", headers: cabecalhos }, cabecalhos);
    if (resposta.status !== 200) return { status: resposta.status, blob: null };
    return { status: 200, blob: await resposta.blob() };
  }

  async function enviar(caminho, opcoes, cabecalhos) {
    const token = obterToken();
    if (token) cabecalhos.Authorization = `Bearer ${token}`;
    try {
      return await fetchFn(`${baseUrl}${caminho}`, opcoes);
    } catch (erro) {
      throw new ErroDeConexao(erro);
    }
  }
  return { requisitar, baixar };
}

async function lerCorpo(resposta) {
  if (resposta.status === 204) return null;
  try {
    return await resposta.json();
  } catch {
    return null;
  }
}
