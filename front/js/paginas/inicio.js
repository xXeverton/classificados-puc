import {
  contarFiltrosAtivos,
  dadosDoCard,
  lerFaixaDePreco,
  mensagemDeFeedVazio,
  montarParametrosFeed,
  paginasNumeradas,
  paramsSemFiltros,
  parametrosDoFeed,
} from "../dominio/feed.js";
import { listarAnuncios } from "../fluxos/listar_anuncios.js";
import { sair } from "../fluxos/sessao_atual.js";
import { ROTAS, irPara, mostrarAlerta, montarDependencias, criar, limparAlerta } from "./comum.js";

const deps = montarDependencias();
const alerta = document.querySelector("#alerta");
const botaoSair = document.querySelector("#sair");
const conteudo = document.querySelector("#conteudo");
const grade = document.querySelector("#grade-anuncios");
const estadoVazio = document.querySelector("#estado-vazio");
const paginacao = document.querySelector("#paginacao");
const busca = document.querySelector("#busca-feed");
const termoBusca = document.querySelector("#termo-busca");
const filtros = document.querySelector("#filtros-feed");
const alternarFiltros = document.querySelector("#alternar-filtros");
const contadorFiltros = document.querySelector("#contador-filtros");
const painelFiltros = document.querySelector("#painel-filtros");
const precoMinimo = document.querySelector("#preco-minimo");
const precoMaximo = document.querySelector("#preco-maximo");
const erroFiltros = document.querySelector("#erro-filtros");
const limparFiltros = document.querySelector("#limpar-filtros");

botaoSair.addEventListener("click", async () => {
  botaoSair.disabled = true;
  await sair(deps);
  irPara(ROTAS.entrar);
});

function formatarPreco(valor, aCombinar) {
  if (aCombinar) return "A combinar";
  return new Intl.NumberFormat("pt-BR", {
    style: "currency",
    currency: "BRL",
  }).format(valor);
}

function formatarData(valor) {
  const data = new Date(valor);
  if (Number.isNaN(data.getTime())) return "";
  return new Intl.DateTimeFormat("pt-BR", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
  }).format(data);
}

function criarCard(anuncio) {
  const dados = dadosDoCard(anuncio);
  const card = criar("a", "anuncio");
  card.href = dados.detalhesUrl;

  if (dados.imagem) {
    const imagem = criar("img", "anuncio__imagem");
    imagem.src = dados.imagem;
    imagem.alt = dados.titulo;
    card.append(imagem);
  } else {
    const imagem = criar("div", "anuncio__imagem anuncio__imagem--vazia", "Sem imagem");
    card.append(imagem);
  }

  const corpo = criar("div", "anuncio__corpo");
  corpo.append(criar("span", "etiqueta", dados.categoria));
  corpo.append(criar(
    "span",
    "anuncio__preco",
    formatarPreco(dados.preco, dados.precoACombinar),
  ));
  corpo.append(criar("h2", "anuncio__titulo", dados.titulo));
  if (dados.descricaoResumida) {
    corpo.append(criar("p", "anuncio__descricao", dados.descricaoResumida));
  }
  corpo.append(criar("span", "anuncio__meta", formatarData(dados.data)));
  if (dados.nomeAnunciante) {
    corpo.append(criar("span", "anuncio__meta", dados.nomeAnunciante));
  }
  card.append(corpo);
  return card;
}

function atualizarUrl(params) {
  const url = new URL(window.location.href);
  url.search = montarParametrosFeed(params).toString();
  window.history.replaceState({}, "", url);
}

function renderizarPaginacao(params, totalPaginas) {
  paginacao.replaceChildren();
  if (totalPaginas <= 1) return;

  for (const numero of paginasNumeradas(params.page, totalPaginas)) {
    const botao = criar("button", "paginacao__item", String(numero));
    botao.type = "button";
    botao.setAttribute("aria-label", `Página ${numero}`);
    botao.setAttribute("aria-current", numero === params.page ? "page" : "false");
    if (numero === params.page) botao.disabled = true;
    botao.addEventListener("click", () => aplicar({ ...params, page: numero }));
    paginacao.append(botao);
  }
}

async function carregar(params) {
  limparAlerta(alerta);
  grade.replaceChildren();
  estadoVazio.hidden = true;
  paginacao.replaceChildren();

  const estado = await listarAnuncios(deps, montarParametrosFeed(params));

  if (estado.tipo === "sem_sessao") {
    irPara(ROTAS.entrar, estado.mensagem ? "sessao_expirada" : undefined);
  } else if (estado.tipo === "feed") {
    conteudo.hidden = false;
    for (const anuncio of estado.feed.items) grade.append(criarCard(anuncio));
    if (!estado.feed.items.length) {
      estadoVazio.textContent = mensagemDeFeedVazio(params, estado.feed.message);
      estadoVazio.hidden = false;
    }
    renderizarPaginacao(params, estado.feed.total_pages);
  } else {
    conteudo.hidden = false;
    mostrarAlerta(alerta, "erro", estado.mensagem);
  }
}

let params = parametrosDoFeed(new URLSearchParams(window.location.search));

function formatarPrecoDoCampo(valor) {
  return valor === null ? "" : String(valor).replace(".", ",");
}

function tipoSelecionado() {
  return filtros.querySelector('[aria-pressed="true"]')?.dataset.type ?? "all";
}

function marcarTipo(tipo) {
  for (const botao of filtros.querySelectorAll("[data-type]")) {
    botao.setAttribute("aria-pressed", String(botao.dataset.type === tipo));
  }
}

function mostrarErroFiltros(mensagem) {
  erroFiltros.textContent = mensagem;
  for (const campo of [precoMinimo, precoMaximo]) {
    campo.setAttribute("aria-invalid", String(Boolean(mensagem)));
  }
}

// Puts the applied state back into the controls, so the menu and the
// counter always show what the feed is filtered by.
function sincronizarControles() {
  termoBusca.value = params.search;
  marcarTipo(params.type);
  precoMinimo.value = formatarPrecoDoCampo(params.minPrice);
  precoMaximo.value = formatarPrecoDoCampo(params.maxPrice);
  mostrarErroFiltros("");

  const ativos = contarFiltrosAtivos(params);
  contadorFiltros.textContent = String(ativos);
  contadorFiltros.hidden = ativos === 0;
  alternarFiltros.setAttribute(
    "aria-label",
    ativos ? `Filtros (${ativos} ativos)` : "Filtros",
  );
  limparFiltros.hidden = !params.search && ativos === 0;
}

function aplicar(novosParams) {
  params = novosParams;
  sincronizarControles();
  atualizarUrl(params);
  carregar(params);
}

function abrirFiltros(aberto) {
  painelFiltros.hidden = !aberto;
  alternarFiltros.setAttribute("aria-expanded", String(aberto));
  if (aberto) filtros.querySelector('[aria-pressed="true"]')?.focus();
}

alternarFiltros.addEventListener("click", () => {
  abrirFiltros(painelFiltros.hidden);
});

for (const botao of filtros.querySelectorAll("[data-type]")) {
  botao.addEventListener("click", () => marcarTipo(botao.dataset.type));
}

painelFiltros.addEventListener("submit", (evento) => {
  evento.preventDefault();
  const faixa = lerFaixaDePreco(precoMinimo.value, precoMaximo.value);
  if (faixa.erro) {
    mostrarErroFiltros(faixa.erro);
    precoMinimo.focus();
    return;
  }
  aplicar({ ...params, ...faixa, page: 1, type: tipoSelecionado() });
  abrirFiltros(false);
  alternarFiltros.focus();
});

busca.addEventListener("submit", (evento) => {
  evento.preventDefault();
  aplicar({ ...params, page: 1, search: termoBusca.value.trim() });
});

limparFiltros.addEventListener("click", () => {
  aplicar(paramsSemFiltros());
  termoBusca.focus();
});

sincronizarControles();
await carregar(params);
