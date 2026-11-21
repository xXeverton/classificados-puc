// Helpers de DOM compartilhados pelas páginas. Só textContent e value: dados
// nunca são interpretados como HTML (RN7).

import { API_BASE_URL } from "../config.js";
import { criarClienteHttp } from "../adaptadores/cliente_http.js";
import { criarAuthApi } from "../adaptadores/auth_api.js";
import { criarArmazenamentoSessao } from "../adaptadores/armazenamento_sessao.js";

export function montarDependencias() {
  const armazenamentoSessao = criarArmazenamentoSessao(window.localStorage);
  const cliente = criarClienteHttp({
    fetchFn: (...args) => window.fetch(...args),
    baseUrl: API_BASE_URL,
    obterToken: () => armazenamentoSessao.ler()?.token ?? null,
  });
  return { authApi: criarAuthApi(cliente), armazenamentoSessao };
}

export const ROTAS = {
  entrar: "/entrar/",
  cadastro: "/cadastro/",
  inicio: "/inicio/",
};

export function irPara(rota, aviso) {
  const destino = aviso ? `${rota}?aviso=${encodeURIComponent(aviso)}` : rota;
  window.location.replace(destino);
}

export function criar(tag, classe, texto) {
  const elemento = document.createElement(tag);
  if (classe) elemento.className = classe;
  if (texto !== undefined) elemento.textContent = texto;
  return elemento;
}

export function mostrarAlerta(regiao, tipo, mensagem) {
  regiao.className = `alerta alerta--${tipo}`;
  regiao.textContent = mensagem;
}

export function limparAlerta(regiao) {
  regiao.className = "";
  regiao.textContent = "";
}

function campoDe(formulario, nome) {
  const campo = formulario.elements[nome];
  // Grupo de radios (RadioNodeList): o erro fica ligado ao primeiro radio.
  const entrada = campo instanceof RadioNodeList ? campo[0] : campo;
  const idBase = campo instanceof RadioNodeList ? `campo-${nome}` : entrada.id;
  return { entrada, erro: formulario.querySelector(`#${idBase}-erro`) };
}

export function limparErros(formulario) {
  for (const erro of formulario.querySelectorAll(".campo__erro")) {
    erro.textContent = "";
  }
  for (const entrada of formulario.querySelectorAll("[aria-invalid]")) {
    entrada.removeAttribute("aria-invalid");
  }
}

// Mostra os erros junto a cada campo e foca o primeiro com erro.
export function mostrarErrosDeCampo(formulario, erros) {
  limparErros(formulario);
  let primeiro = null;
  for (const [nome, mensagem] of Object.entries(erros)) {
    const { entrada, erro } = campoDe(formulario, nome);
    erro.textContent = mensagem;
    entrada.setAttribute("aria-invalid", "true");
    entrada.setAttribute("aria-describedby", erro.id);
    primeiro ??= entrada;
  }
  if (primeiro) primeiro.focus();
}

export function carregando(botao, ativo, textoEmAndamento) {
  if (ativo) {
    botao.dataset.textoOriginal = botao.textContent;
    botao.textContent = textoEmAndamento;
    botao.disabled = true;
    botao.setAttribute("aria-busy", "true");
  } else {
    botao.textContent = botao.dataset.textoOriginal ?? botao.textContent;
    botao.disabled = false;
    botao.removeAttribute("aria-busy");
  }
}

// Envolve o envio de um formulário: bloqueia envio duplicado e restaura o botão.
export function aoEnviar(formulario, botao, textoEmAndamento, tratar) {
  let enviando = false;
  formulario.addEventListener("submit", async (evento) => {
    evento.preventDefault();
    if (enviando) return;
    enviando = true;
    carregando(botao, true, textoEmAndamento);
    try {
      await tratar();
    } finally {
      enviando = false;
      carregando(botao, false);
    }
  });
}

export function ativarAlternarSenha(botao, entrada) {
  botao.addEventListener("click", () => {
    const mostrar = entrada.type === "password";
    entrada.type = mostrar ? "text" : "password";
    botao.textContent = mostrar ? "Ocultar" : "Mostrar";
    botao.setAttribute("aria-pressed", String(mostrar));
  });
}

export function ativarTodosOsAlternadoresDeSenha(formulario) {
  for (const botao of formulario.querySelectorAll(".campo-senha__alternar")) {
    const entrada = botao.parentElement.querySelector("input");
    ativarAlternarSenha(botao, entrada);
  }
}

export function apagarSenhas(formulario, ...nomes) {
  for (const nome of nomes) {
    const entrada = formulario.elements[nome];
    entrada.value = "";
    entrada.type = "password";
    const botao = entrada.parentElement.querySelector(".campo-senha__alternar");
    if (botao) {
      botao.textContent = "Mostrar";
      botao.setAttribute("aria-pressed", "false");
    }
  }
}
