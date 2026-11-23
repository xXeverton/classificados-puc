import {
  criar,
  irPara,
  ligarBotaoSair,
  mostrarAlerta,
  montarDependencias,
  ROTAS,
} from "./comum.js";
import { API_BASE_URL } from "../config.js";
import { resolverUrlRecurso } from "../dominio/detalhes_anuncio.js";
import { rotaEditarAnuncio } from "../dominio/rotas.js";
import { SECOES_DO_PAINEL, acoesDoAnuncio } from "../dominio/meus_anuncios.js";
import { chamarApi } from "../fluxos/conexao.js";
import { carregarUsuario } from "../fluxos/sessao_atual.js";

const deps = montarDependencias();
ligarBotaoSair(document.querySelector("#sair"), deps);

const alerta = document.querySelector("#alerta");
const conteudo = document.querySelector("#conteudo");
const usuario = await carregarUsuario(deps);
if (usuario.tipo !== "logado") {
  irPara(ROTAS.entrar, usuario.mensagem ? "sessao_expirada" : undefined);
} else {
  conteudo.hidden = false;
  await carregarTodas();
}

async function carregarTodas() {
  for (const secao of SECOES_DO_PAINEL) {
    await carregarSecao(secao, 1);
  }
}

async function carregarSecao(secao, page) {
  const grade = document.querySelector(`#${secao.lista}`);
  const paginacao = document.querySelector(`#${secao.paginacao}`);
  const vazio = document.querySelector(`#${secao.vazio}`);
  grade.replaceChildren();
  paginacao.replaceChildren();

  const { resposta, falha } = await chamarApi(
    () => deps.adsApi.listarMeus(secao.status, page),
  );
  if (falha) {
    mostrarAlerta(alerta, "erro", "Não foi possível carregar seus anúncios.");
    return;
  }
  if (resposta.status === 401) {
    irPara(ROTAS.entrar, "sessao_expirada");
    return;
  }
  if (resposta.status !== 200) {
    mostrarAlerta(alerta, "erro", resposta.corpo?.message ?? "Não foi possível carregar seus anúncios.");
    return;
  }

  vazio.hidden = resposta.corpo.items.length !== 0;
  vazio.textContent = secao.textoVazio;
  for (const anuncio of resposta.corpo.items) {
    grade.append(criarCard(anuncio, secao.status));
  }
  renderizarPaginacao(paginacao, secao, resposta.corpo.page, resposta.corpo.total_pages);
}

function criarCard(anuncio, status) {
  const card = criar("article", "meus-anuncios__card");
  if (anuncio.image_url) {
    const imagem = criar("img", "meus-anuncios__imagem");
    imagem.src = resolverUrlRecurso(anuncio.image_url, API_BASE_URL);
    imagem.alt = anuncio.title;
    card.append(imagem);
  } else {
    card.append(criar("div", "meus-anuncios__imagem meus-anuncios__imagem--vazia", "Sem imagem"));
  }
  const corpo = criar("div", "meus-anuncios__corpo");
  corpo.append(criar("span", "etiqueta", anuncio.category));
  corpo.append(criar("h2", "meus-anuncios__titulo", anuncio.title));
  corpo.append(criar("p", "meus-anuncios__preco",
    anuncio.preco_a_combinar
      ? "A combinar"
      : new Intl.NumberFormat("pt-BR", { style: "currency", currency: "BRL" }).format(anuncio.price),
  ));
  const acoes = criar("div", "acoes");
  for (const acao of acoesDoAnuncio(status)) {
    acoes.append(criarBotaoDeAcao(acao, anuncio));
  }
  corpo.append(acoes);
  card.append(corpo);
  return card;
}

function criarBotaoDeAcao(acao, anuncio) {
  const classe = `botao botao--${acao.estilo}`;
  if (acao.tipo === "editar") {
    const editar = criar("a", classe, acao.rotulo);
    editar.href = rotaEditarAnuncio(anuncio.id);
    return editar;
  }
  const botao = criar("button", classe, acao.rotulo);
  botao.type = "button";
  const executar = {
    excluir: () => excluirAnuncio(anuncio.id),
    renovar: () => renovarAnuncio(anuncio.id),
    vender: () => alterarStatus(anuncio.id, acao),
    reativar: () => alterarStatus(anuncio.id, acao),
  }[acao.tipo];
  botao.addEventListener("click", executar);
  return botao;
}

function renderizarPaginacao(navegacao, secao, paginaAtual, totalPaginas) {
  if (totalPaginas <= 1) return;
  for (let pagina = 1; pagina <= totalPaginas; pagina += 1) {
    const botao = criar("button", "paginacao__item", String(pagina));
    botao.type = "button";
    botao.disabled = pagina === paginaAtual;
    botao.addEventListener("click", () => carregarSecao(secao, pagina));
    navegacao.append(botao);
  }
}

async function excluirAnuncio(id) {
  if (!window.confirm("Deseja excluir este anúncio definitivamente?")) return;
  const { resposta, falha } = await chamarApi(
    () => deps.adsApi.excluir(id),
  );
  if (falha || resposta.status !== 204) {
    mostrarAlerta(alerta, "erro", "Não foi possível excluir o anúncio.");
    return;
  }
  mostrarAlerta(alerta, "sucesso", "Anúncio excluído.");
  await carregarTodas();
}

async function renovarAnuncio(id) {
  if (!window.confirm("Deseja renovar este anúncio por 30 dias?")) return;
  const { resposta, falha } = await chamarApi(
    () => deps.adsApi.renovar(id),
  );
  if (falha || resposta.status !== 200) {
    mostrarAlerta(alerta, "erro", resposta?.corpo?.message ?? "Não foi possível renovar o anúncio.");
    return;
  }
  mostrarAlerta(alerta, "sucesso", "Anúncio renovado por 30 dias.");
  await carregarTodas();
}

async function alterarStatus(id, acao) {
  if (!window.confirm(acao.confirmacao)) return;
  const { resposta, falha } = await chamarApi(
    () => deps.adsApi.alterarStatus(id, acao.novoStatus),
  );
  if (falha || resposta.status !== 200) {
    mostrarAlerta(alerta, "erro", resposta?.corpo?.message ?? "Não foi possível alterar o anúncio.");
    return;
  }
  mostrarAlerta(alerta, "sucesso", acao.sucesso);
  await carregarTodas();
}
