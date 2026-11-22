// Helpers de DOM compartilhados pelas páginas. Só textContent e value: dados
// nunca são interpretados como HTML (RN7).

import { API_BASE_URL } from "../config.js";
import { criarClienteHttp } from "../adaptadores/cliente_http.js";
import { criarAuthApi } from "../adaptadores/auth_api.js";
import { criarPerfilApi } from "../adaptadores/perfil_api.js";
import { criarAdsApi } from "../adaptadores/ads_api.js";
import { sair } from "../fluxos/sessao_atual.js";
import { criarArmazenamentoSessao } from "../adaptadores/armazenamento_sessao.js";

export function montarDependencias() {
  const armazenamentoSessao = criarArmazenamentoSessao(window.localStorage);
  const cliente = criarClienteHttp({
    fetchFn: (...args) => window.fetch(...args),
    baseUrl: API_BASE_URL,
    obterToken: () => armazenamentoSessao.ler()?.token ?? null,
  });
  return {
    authApi: criarAuthApi(cliente),
    perfilApi: criarPerfilApi(cliente),
    adsApi: criarAdsApi(cliente),
    armazenamentoSessao,
  };
}

export const ROTAS = {
  entrar: "/entrar/",
  cadastro: "/cadastro/",
  inicio: "/inicio/",
  perfil: "/perfil/",
  editarPerfilAnunciante: "/perfil/anunciante/",
  novoAnuncio: "/anuncios/novo/",
  meusAnuncios: "/meus-anuncios/",
};

export function ligarBotaoSair(botao, deps) {
  botao.addEventListener("click", async () => {
    botao.disabled = true;
    await sair(deps);
    irPara(ROTAS.entrar);
  });
}

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
  const ehGrupo = campo instanceof RadioNodeList;
  const entrada = ehGrupo ? campo[0] : campo;
  if (!entrada) return { entrada: null, erro: null };
  const idBase = ehGrupo ? `campo-${nome}` : entrada.id;
  return { entrada, erro: formulario.querySelector(`#${idBase}-erro`) };
}

export function limparErros(formulario) {
  const erros = [...formulario.querySelectorAll(".campo__erro")];
  const idsDeErro = new Set(erros.map((erro) => erro.id));
  for (const erro of erros) {
    erro.textContent = "";
  }
  for (const entrada of formulario.querySelectorAll("[aria-describedby]")) {
    const ids = entrada.getAttribute("aria-describedby")
      .split(/\s+/)
      .filter((id) => !idsDeErro.has(id));
    if (ids.length) entrada.setAttribute("aria-describedby", ids.join(" "));
    else entrada.removeAttribute("aria-describedby");
  }
  for (const entrada of formulario.querySelectorAll("[aria-invalid]")) {
    entrada.removeAttribute("aria-invalid");
  }
}

export function mostrarErroDeCampo(formulario, nome, mensagem) {
  const { entrada, erro } = campoDe(formulario, nome);
  if (!entrada || !erro) return false;
  erro.textContent = mensagem;
  entrada.setAttribute("aria-invalid", "true");
  const ids = (entrada.getAttribute("aria-describedby") ?? "")
    .split(/\s+/)
    .filter(Boolean);
  if (!ids.includes(erro.id)) ids.push(erro.id);
  entrada.setAttribute("aria-describedby", ids.join(" "));
  return true;
}

export function limparErroDeCampo(formulario, nome) {
  const { entrada, erro } = campoDe(formulario, nome);
  if (!entrada || !erro) return;
  erro.textContent = "";
  entrada.removeAttribute("aria-invalid");
  const ids = (entrada.getAttribute("aria-describedby") ?? "")
    .split(/\s+/)
    .filter((id) => id && id !== erro.id);
  if (ids.length) entrada.setAttribute("aria-describedby", ids.join(" "));
  else entrada.removeAttribute("aria-describedby");
}

// Mostra os erros junto a cada campo e foca o primeiro com erro.
export function mostrarErrosDeCampo(formulario, erros) {
  limparErros(formulario);
  let primeiro = null;
  for (const [nome, mensagem] of Object.entries(erros)) {
    const { entrada } = campoDe(formulario, nome);
    if (mostrarErroDeCampo(formulario, nome, mensagem)) {
      primeiro ??= entrada;
    }
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
