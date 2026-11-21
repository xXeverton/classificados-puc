import { ErroDeConexao } from "../dominio/erros.js";

export function criarClienteHttp({ fetchFn, baseUrl, obterToken = () => null }) {
  async function requisitar(metodo, caminho, corpo) {
    const cabecalhos = { Accept: "application/json" };
    const opcoes = { method: metodo, headers: cabecalhos };
    if (corpo !== undefined) {
      cabecalhos["Content-Type"] = "application/json";
      opcoes.body = JSON.stringify(corpo);
    }
    const token = obterToken();
    if (token) cabecalhos.Authorization = `Bearer ${token}`;

    let resposta;
    try {
      resposta = await fetchFn(`${baseUrl}${caminho}`, opcoes);
    } catch (erro) {
      throw new ErroDeConexao(erro);
    }
    return { status: resposta.status, corpo: await lerCorpo(resposta) };
  }
  return { requisitar };
}

async function lerCorpo(resposta) {
  if (resposta.status === 204) return null;
  try {
    return await resposta.json();
  } catch {
    return null;
  }
}
