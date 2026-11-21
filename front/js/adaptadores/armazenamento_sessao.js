export const CHAVE_SESSAO = "classificados.sessao";

export function criarArmazenamentoSessao(storage, agora = () => Date.now()) {
  function apagar() {
    storage.removeItem(CHAVE_SESSAO);
  }

  function salvar({ token, expira_em }) {
    storage.setItem(CHAVE_SESSAO, JSON.stringify({ token, expira_em }));
  }

  // motivo: "ausente" (nunca houve sessão ou dado corrompido) ou "expirada".
  function lerComMotivo() {
    const bruto = storage.getItem(CHAVE_SESSAO);
    if (!bruto) return { sessao: null, motivo: "ausente" };
    let sessao;
    try {
      sessao = JSON.parse(bruto);
    } catch {
      apagar();
      return { sessao: null, motivo: "ausente" };
    }
    const expiraEm = Date.parse(sessao?.expira_em);
    if (!sessao?.token || Number.isNaN(expiraEm)) {
      apagar();
      return { sessao: null, motivo: "ausente" };
    }
    if (expiraEm <= agora()) {
      apagar();
      return { sessao: null, motivo: "expirada" };
    }
    return { sessao, motivo: null };
  }

  const ler = () => lerComMotivo().sessao;

  return { salvar, ler, lerComMotivo, apagar };
}
