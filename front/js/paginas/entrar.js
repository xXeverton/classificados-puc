import { entrar } from "../fluxos/entrar.js";
import { haSessao } from "../fluxos/sessao_atual.js";
import { MENSAGENS } from "../dominio/mensagens.js";
import {
  ROTAS,
  aoEnviar,
  apagarSenhas,
  ativarTodosOsAlternadoresDeSenha,
  irPara,
  limparAlerta,
  limparErros,
  mostrarAlerta,
  mostrarErrosDeCampo,
  montarDependencias,
} from "./comum.js";
import { ligarReenvio } from "./reenvio.js";

const deps = montarDependencias();

if (haSessao(deps)) {
  irPara(ROTAS.inicio);
}

const formulario = document.querySelector("#form-entrar");
const alerta = document.querySelector("#alerta");
const reenvio = ligarReenvio(deps, document.querySelector("#reenvio"));

ativarTodosOsAlternadoresDeSenha(formulario);

if (new URLSearchParams(window.location.search).get("aviso") === "sessao_expirada") {
  mostrarAlerta(alerta, "aviso", MENSAGENS.sessaoExpirada);
}

aoEnviar(formulario, formulario.querySelector("button[type=submit]"), "Entrando…", async () => {
  limparAlerta(alerta);
  reenvio.ocultar();
  const estado = await entrar(deps, {
    identificador: formulario.elements.identificador.value,
    senha: formulario.elements.senha.value,
  });

  if (estado.tipo === "sucesso") {
    irPara(ROTAS.inicio);
    return;
  }
  if (estado.tipo === "validacao") {
    mostrarErrosDeCampo(formulario, estado.erros);
    return;
  }

  limparErros(formulario);
  if (estado.tipo === "conexao") {
    mostrarAlerta(alerta, "erro", estado.mensagem);
    return;
  }

  apagarSenhas(formulario, "senha");
  if (estado.tipo === "email_nao_confirmado") {
    mostrarAlerta(alerta, "aviso", estado.mensagem);
    const identificador = formulario.elements.identificador.value.trim();
    reenvio.mostrar(identificador.includes("@") ? identificador : "");
  } else if (estado.tipo === "bloqueado") {
    mostrarAlerta(alerta, "aviso", estado.mensagem);
  } else {
    mostrarAlerta(alerta, "erro", estado.mensagem);
  }
  formulario.elements.senha.focus();
});
