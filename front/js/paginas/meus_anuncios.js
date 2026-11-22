import {
  criar,
  irPara,
  ligarBotaoSair,
  mostrarAlerta,
  montarDependencias,
  ROTAS,
} from "./comum.js";
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
  await carregarStatus("published", "publicados", "paginacao-publicados", "vazio-publicados");
  await carregarStatus("expired", "expirados", "paginacao-expirados", "vazio-expirados");
}

async function carregarStatus(status, gradeId, paginacaoId, vazioId) {
  const grade = document.querySelector(`#${gradeId}`);
  const paginacao = document.querySelector(`#${paginacaoId}`);
  const vazio = document.querySelector(`#${vazioId}`);
  grade.replaceChildren();
  paginacao.replaceChildren();

  const { resposta, falha } = await chamarApi(
    () => deps.adsApi.listarMeus(status),
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
  vazio.textContent = status === "published"
    ? "Você ainda não possui anúncios publicados."
    : "Você não possui anúncios expirados.";

  for (const anuncio of resposta.corpo.items) {
    grade.append(criarCard(anuncio, status));
  }
  renderizarPaginacao(paginacao, status, resposta.corpo.page, resposta.corpo.total_pages);
}

function criarCard(anuncio, status) {
  const card = criar("article", "meus-anuncios__card");
  if (anuncio.image_url) {
    const imagem = criar("img", "meus-anuncios__imagem");
    imagem.src = anuncio.image_url;
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

  const editar = criar("a", "botao botao--contorno", "Editar");
  editar.href = `/anuncios/novo/?editar=${anuncio.id}`;
  acoes.append(editar);

  const excluir = criar("button", "botao botao--contorno", "Excluir");
  excluir.type = "button";
  excluir.addEventListener("click", () => excluirAnuncio(anuncio.id));
  acoes.append(excluir);

  if (status === "expired") {
    const renovar = criar("button", "botao botao--primario", "Renovar");
    renovar.type = "button";
    renovar.addEventListener("click", () => renovarAnuncio(anuncio.id));
    acoes.append(renovar);
  }

  corpo.append(acoes);
  card.append(corpo);
  return card;
}

function renderizarPaginacao(navegacao, status, paginaAtual, totalPaginas) {
  if (totalPaginas <= 1) return;
  for (let pagina = 1; pagina <= totalPaginas; pagina += 1) {
    const botao = criar("button", "paginacao__item", String(pagina));
    botao.type = "button";
    botao.disabled = pagina === paginaAtual;
    botao.addEventListener("click", async () => {
      const gradeId = status === "published" ? "publicados" : "expirados";
      const vazioId = status === "published" ? "vazio-publicados" : "vazio-expirados";
      await carregarPaginaStatus(status, gradeId, navegacao.id, vazioId, pagina);
    });
    navegacao.append(botao);
  }
}

async function carregarPaginaStatus(status, gradeId, paginacaoId, vazioId, page) {
  const grade = document.querySelector(`#${gradeId}`);
  const paginacao = document.querySelector(`#${paginacaoId}`);
  const vazio = document.querySelector(`#${vazioId}`);
  grade.replaceChildren();
  paginacao.replaceChildren();
  const { resposta, falha } = await chamarApi(
    () => deps.adsApi.listarMeus(status, page),
  );
  if (falha || resposta.status !== 200) {
    mostrarAlerta(alerta, "erro", "Não foi possível carregar seus anúncios.");
    return;
  }
  vazio.hidden = resposta.corpo.items.length !== 0;
  for (const anuncio of resposta.corpo.items) grade.append(criarCard(anuncio, status));
  renderizarPaginacao(paginacao, status, resposta.corpo.page, resposta.corpo.total_pages);
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
  await carregarStatus("published", "publicados", "paginacao-publicados", "vazio-publicados");
  await carregarStatus("expired", "expirados", "paginacao-expirados", "vazio-expirados");
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
  await carregarStatus("published", "publicados", "paginacao-publicados", "vazio-publicados");
  await carregarStatus("expired", "expirados", "paginacao-expirados", "vazio-expirados");
}
