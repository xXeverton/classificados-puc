import { ErroDeConexao } from "../js/dominio/erros.js";

export function criarFetchFalso(respostas = []) {
  const chamadas = [];
  const fila = [...respostas];
  async function fetchFn(url, opcoes) {
    chamadas.push({ url, opcoes });
    const proxima = fila.shift();
    if (proxima instanceof Error) throw proxima;
    const { status, corpo } = proxima ?? { status: 200, corpo: {} };
    return {
      status,
      json: async () => {
        if (corpo === undefined) throw new Error("sem corpo");
        return corpo;
      },
    };
  }
  return { fetchFn, chamadas };
}

export function criarStorageEmMemoria() {
  const dados = new Map();
  return {
    getItem: (k) => (dados.has(k) ? dados.get(k) : null),
    setItem: (k, v) => dados.set(k, String(v)),
    removeItem: (k) => dados.delete(k),
  };
}

export function criarAuthApiFalsa(respostas = {}) {
  const chamadas = [];
  const api = {};
  for (const nome of ["cadastrar", "confirmar", "reenviar", "login", "logout", "me"]) {
    api[nome] = async (...args) => {
      chamadas.push({ nome, args });
      const resposta = respostas[nome];
      if (resposta instanceof Error) throw resposta;
      return resposta ?? { status: 200, corpo: {} };
    };
  }
  api.chamadas = chamadas;
  return api;
}

export function criarPerfilApiFalso(respostas = {}) {
  const chamadas = [];
  const api = {};
  for (const nome of ["obter", "salvar", "foto"]) {
    api[nome] = async (...args) => {
      chamadas.push({ nome, args });
      const resposta = respostas[nome];
      if (resposta instanceof Error) throw resposta;
      return resposta ?? { status: 200, corpo: {} };
    };
  }
  api.chamadas = chamadas;
  return api;
}

export function criarArmazenamentoFalso(sessao = null, motivo = "ausente") {
  const estado = { sessao, salvos: [], apagado: 0 };
  return {
    estado,
    salvar: (s) => { estado.sessao = s; estado.salvos.push(s); },
    ler: () => estado.sessao,
    lerComMotivo: () => ({
      sessao: estado.sessao,
      motivo: estado.sessao ? null : motivo,
    }),
    apagar: () => { estado.sessao = null; estado.apagado += 1; },
  };
}

export const conexaoCaida = () => new ErroDeConexao(new Error("rede"));
