import { confirmarEmail } from "../fluxos/confirmar_email.js";
import { ROTAS, carregando, mostrarAlerta, montarDependencias } from "./comum.js";
import { ligarReenvio } from "./reenvio.js";

const deps = montarDependencias();
const token = new URLSearchParams(window.location.search).get("token");

const alerta = document.querySelector("#alerta");
const botao = document.querySelector("#confirmar");
const caminhos = document.querySelector("#caminhos");
const linkEntrar = document.querySelector("#link-entrar");
const linkCadastro = document.querySelector("#link-cadastro");
const reenvio = ligarReenvio(deps, document.querySelector("#reenvio"));

function mostrarCaminhos({ entrar, cadastro }) {
  linkEntrar.hidden = !entrar;
  linkCadastro.hidden = !cadastro;
  caminhos.hidden = false;
}

const TELAS = {
  confirmado() {
    mostrarAlerta(alerta, "sucesso", "E-mail confirmado. Você já pode entrar.");
    mostrarCaminhos({ entrar: true });
  },
  expirado() {
    mostrarAlerta(alerta, "aviso", "O link expirou. Informe seu e-mail para receber um novo.");
    reenvio.mostrar();
  },
  invalido() {
    mostrarAlerta(alerta, "erro", "Este link não é válido: já foi usado ou está incorreto.");
    mostrarCaminhos({ entrar: true, cadastro: true });
  },
  conexao: (estado) => mostrarAlerta(alerta, "erro", estado.mensagem),
  erro_servidor: (estado) => mostrarAlerta(alerta, "erro", estado.mensagem),
};

if (!token) {
  mostrarAlerta(alerta, "erro", "O link de confirmação está incompleto.");
  botao.hidden = true;
  mostrarCaminhos({ entrar: true, cadastro: true });
} else {
  botao.addEventListener("click", async () => {
    if (botao.disabled) return;
    carregando(botao, true, "Confirmando…");
    const estado = await confirmarEmail(deps, token);
    carregando(botao, false);
    if (estado.tipo === "conexao" || estado.tipo === "erro_servidor") {
      TELAS[estado.tipo](estado);
      return;
    }
    botao.hidden = true;
    TELAS[estado.tipo](estado);
  });
}

linkEntrar.href = ROTAS.entrar;
linkCadastro.href = ROTAS.cadastro;
