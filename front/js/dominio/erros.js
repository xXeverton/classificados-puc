export class ErroDeConexao extends Error {
  constructor(causa) {
    super("Falha de conexão com o servidor.");
    this.name = "ErroDeConexao";
    this.causa = causa;
  }
}
