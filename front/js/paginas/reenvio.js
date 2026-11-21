import { reenviarConfirmacao } from "../fluxos/reenviar_confirmacao.js";
import {
  aoEnviar,
  limparErros,
  mostrarAlerta,
  mostrarErrosDeCampo,
} from "./comum.js";

// Liga o formulário de reenvio do link (usado em entrada, cadastro e confirmação).
export function ligarReenvio(deps, formulario) {
  const aviso = formulario.querySelector("[data-aviso]");
  const botao = formulario.querySelector("button[type=submit]");

  aoEnviar(formulario, botao, "Enviando…", async () => {
    aviso.className = "";
    aviso.textContent = "";
    const estado = await reenviarConfirmacao(deps, formulario.elements.email.value);
    if (estado.tipo === "validacao") {
      mostrarErrosDeCampo(formulario, estado.erros);
      return;
    }
    limparErros(formulario);
    const tipo = estado.tipo === "reenviado" ? "sucesso" : "erro";
    mostrarAlerta(aviso, tipo, estado.mensagem);
  });

  return {
    mostrar(email = "") {
      if (email) formulario.elements.email.value = email;
      formulario.hidden = false;
    },
    ocultar() {
      formulario.hidden = true;
    },
  };
}
