export function criarAuthApi(cliente) {
  const { requisitar } = cliente;
  return {
    cadastrar: (dados) => requisitar("POST", "/auth/cadastro", dados),
    confirmar: (token) => requisitar("POST", "/auth/confirmacao", { token }),
    reenviar: (email) =>
      requisitar("POST", "/auth/confirmacao/reenviar", { email }),
    login: (identificador, senha) =>
      requisitar("POST", "/auth/login", { identificador, senha }),
    logout: () => requisitar("POST", "/auth/logout"),
    me: () => requisitar("GET", "/auth/me"),
  };
}
