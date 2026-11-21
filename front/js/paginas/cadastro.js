import { cadastrar } from "../fluxos/cadastrar.js";
import { haSessao } from "../fluxos/sessao_atual.js";
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

const secaoFormulario = document.querySelector("#secao-formulario");
const secaoVerifique = document.querySelector("#secao-verifique");
const formulario = document.querySelector("#form-cadastro");
const alerta = document.querySelector("#alerta");
const reenvio = ligarReenvio(deps, document.querySelector("#reenvio"));

ativarTodosOsAlternadoresDeSenha(formulario);

function lerDados() {
  const campos = formulario.elements;
  return {
    nome: campos.nome.value,
    email: campos.email.value,
    nome_usuario: campos.nome_usuario.value,
    vinculo: campos.vinculo.value,
    matricula: campos.matricula.value,
    senha: campos.senha.value,
    confirmacao_senha: campos.confirmacao_senha.value,
  };
}

aoEnviar(formulario, formulario.querySelector("button[type=submit]"), "Cadastrando…", async () => {
  limparAlerta(alerta);
  const estado = await cadastrar(deps, lerDados());

  if (estado.tipo === "validacao") {
    mostrarErrosDeCampo(formulario, estado.erros);
    return;
  }
  limparErros(formulario);

  if (estado.tipo === "verifique_email") {
    apagarSenhas(formulario, "senha", "confirmacao_senha");
    document.querySelector("#email-enviado").textContent = estado.email;
    secaoFormulario.hidden = true;
    secaoVerifique.hidden = false;
    reenvio.mostrar(estado.email);
    secaoVerifique.querySelector("h1").focus();
    return;
  }

  if (estado.tipo === "erro_servidor") {
    apagarSenhas(formulario, "senha", "confirmacao_senha");
  }
  mostrarAlerta(alerta, "erro", estado.mensagem);
});
