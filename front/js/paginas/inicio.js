import { dadosDoCard, paginasNumeradas } from "../dominio/feed.js";
import { API_BASE_URL } from "../config.js";
import { resolverUrlRecurso } from "../dominio/detalhes_anuncio.js";
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
    imagem.src = resolverUrlRecurso(dados.imagem, API_BASE_URL);
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
  url.search = "";
  url.searchParams.set("page", String(params.page));
  if (params.search) url.searchParams.set("search", params.search);
  if (params.type !== "all") url.searchParams.set("type", params.type);
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
    botao.addEventListener("click", () => {
      const novosParams = { ...params, page: numero };
      atualizarUrl(novosParams);
      carregar(novosParams);
    });
    paginacao.append(botao);
  }
}

async function carregar(params) {
  limparAlerta(alerta);
  grade.replaceChildren();
  estadoVazio.hidden = true;
  paginacao.replaceChildren();

  const estado = await listarAnuncios(deps, new URLSearchParams({
    page: String(params.page),
    ...(params.search ? { search: params.search } : {}),
    ...(params.type !== "all" ? { type: params.type } : {}),
  }));

  if (estado.tipo === "sem_sessao") {
    irPara(ROTAS.entrar, estado.mensagem ? "sessao_expirada" : undefined);
  } else if (estado.tipo === "feed") {
    conteudo.hidden = false;
    for (const anuncio of estado.feed.items) grade.append(criarCard(anuncio));
    if (!estado.feed.items.length) {
      estadoVazio.textContent = estado.feed.message || "Nenhum anúncio publicado encontrado.";
      estadoVazio.hidden = false;
    }
    renderizarPaginacao(params, estado.feed.total_pages);
  } else {
    conteudo.hidden = false;
    mostrarAlerta(alerta, "erro", estado.mensagem);
  }
}

const parametrosIniciais = new URLSearchParams(window.location.search);
const params = {
  page: Math.max(1, Number(parametrosIniciais.get("page") || 1)),
  search: parametrosIniciais.get("search") || "",
  type: ["all", "product", "service", "event"].includes(parametrosIniciais.get("type"))
    ? parametrosIniciais.get("type")
    : "all",
};
termoBusca.value = params.search;
for (const botao of filtros.querySelectorAll("[data-type]")) {
  botao.setAttribute("aria-pressed", String(botao.dataset.type === params.type));
}

busca.addEventListener("submit", (evento) => {
  evento.preventDefault();
  const novosParams = { ...params, page: 1, search: termoBusca.value.trim() };
  params.page = novosParams.page;
  params.search = novosParams.search;
  atualizarUrl(novosParams);
  carregar(novosParams);
});

for (const botao of filtros.querySelectorAll("[data-type]")) {
  botao.addEventListener("click", () => {
    const novosParams = { ...params, page: 1, type: botao.dataset.type };
    params.page = novosParams.page;
    params.type = novosParams.type;
    for (const opcao of filtros.querySelectorAll("[data-type]")) {
      opcao.setAttribute("aria-pressed", String(opcao === botao));
    }
    atualizarUrl(novosParams);
    carregar(novosParams);
  });
}

await carregar(params);
