import {
  idDoAnuncio,
  formatarPrecoDetalhes,
  rotuloConservacao,
  rotuloContato,
  resolverUrlRecurso,
  hrefContato,
  classificarContatosPrincipais,
} from "../dominio/detalhes_anuncio.js";
import { detalharAnuncio } from "../fluxos/detalhar_anuncio.js";
import { criarCarregadorDeFoto } from "../fluxos/carregar_foto.js";
import { API_BASE_URL } from "../config.js";
import {
  criar,
  irPara,
  ligarBotaoSair,
  mostrarAlerta,
  montarDependencias,
  limparAlerta,
} from "./comum.js";

const deps = montarDependencias();
ligarBotaoSair(document.querySelector("#sair"), deps);

const alerta = document.querySelector("#alerta");
const carregando = document.querySelector("#carregando");
const conteudo = document.querySelector("#conteudo");
const fotoAnuncio = document.querySelector("#foto-anuncio");
const semFoto = document.querySelector("#sem-foto");
const fotoAnunciante = document.querySelector("#foto-anunciante");
const contatos = document.querySelector("#contatos");
const carregadorFoto = criarCarregadorDeFoto(deps);

function mostrarEstado(mensagem) {
  carregando.hidden = true;
  conteudo.hidden = true;
  mostrarAlerta(alerta, "erro", mensagem);
}

function renderizarContatos(lista, titulo) {
  contatos.replaceChildren();

  const principais = classificarContatosPrincipais(lista, titulo);

  if (principais.whatsapp) {
    const link = criar("a", "botao botao--contorno detalhes__contato", "Chamar no WhatsApp");
    link.href = principais.whatsapp;
    link.target = "_blank";
    link.rel = "noopener noreferrer";
    link.setAttribute("aria-label", "Chamar no WhatsApp");
    contatos.append(link);
  }

  if (principais.email) {
    const link = criar("a", "botao botao--contorno detalhes__contato", "Enviar E-mail");
    link.href = principais.email;
    link.target = "_blank";
    link.rel = "noopener noreferrer";
    link.setAttribute("aria-label", "Enviar E-mail");
    contatos.append(link);
  }

  if (!principais.whatsapp && !principais.email) {
    const whatsappDesabilitado = criar(
      "button",
      "botao botao--contorno detalhes__contato",
      "Chamar no WhatsApp",
    );
    whatsappDesabilitado.type = "button";
    whatsappDesabilitado.disabled = true;
    whatsappDesabilitado.setAttribute("aria-label", "Chamar no WhatsApp indisponível");
    contatos.append(whatsappDesabilitado);

    const emailDesabilitado = criar(
      "button",
      "botao botao--contorno detalhes__contato",
      "Enviar E-mail",
    );
    emailDesabilitado.type = "button";
    emailDesabilitado.disabled = true;
    emailDesabilitado.setAttribute("aria-label", "Enviar E-mail indisponível");
    contatos.append(emailDesabilitado);
  }

  for (const contato of lista) {
    if (contato.tipo === "whatsapp" || contato.tipo === "email") continue;
    const link = criar("a", "botao botao--contorno detalhes__contato", rotuloContato(contato));
    link.href = hrefContato(contato, titulo);
    link.target = "_blank";
    link.rel = "noopener noreferrer";
    link.setAttribute("aria-label", `${rotuloContato(contato)}: ${contato.valor}`);
    contatos.append(link);
  }
}

async function carregar() {
  limparAlerta(alerta);
  const id = idDoAnuncio(window.location.search);
  if (id === null) {
    mostrarEstado("Anúncio não encontrado.");
    return;
  }

  const estado = await detalharAnuncio(deps, id);
  if (estado.tipo === "sem_sessao") {
    irPara(ROTAS.entrar, "sessao_expirada");
    return;
  }
  if (estado.tipo === "conexao") {
    mostrarEstado("Não foi possível carregar o anúncio. Tente novamente.");
    return;
  }
  if (estado.tipo !== "detalhes") {
    mostrarEstado(estado.mensagem);
    return;
  }

  const dados = estado.detalhes;
  const ad = dados.ad;
  document.querySelector("#categoria").textContent = ad.category;
  document.querySelector("#titulo").textContent = ad.title;
  document.querySelector("#preco").textContent =
    formatarPrecoDetalhes(ad.price, ad.preco_a_combinar);
  document.querySelector("#descricao").textContent = ad.description || "";

  const conservacao = rotuloConservacao(ad.estado_conservacao);
  const linhaConservacao = document.querySelector("#linha-conservacao");
  if (conservacao) {
    document.querySelector("#conservacao").textContent = conservacao;
    linhaConservacao.hidden = false;
  } else {
    linhaConservacao.hidden = true;
  }

  if (ad.image_url) {
    fotoAnuncio.src = resolverUrlRecurso(ad.image_url, API_BASE_URL);
    fotoAnuncio.alt = ad.title;
    fotoAnuncio.hidden = false;
    semFoto.hidden = true;
  } else {
    fotoAnuncio.hidden = true;
    semFoto.hidden = false;
  }

  const advertiser = dados.advertiser;
  document.querySelector("#nome-anunciante").textContent =
    advertiser.display_name;
  document.querySelector("#vinculo").textContent =
    advertiser.affiliation === "aluno" ? "Aluno" : "Funcionário";
  const blobFoto = await carregadorFoto.carregar(advertiser.photo_url);
  if (blobFoto) {
    fotoAnunciante.src = blobFoto;
    fotoAnunciante.alt = `Foto de ${advertiser.display_name}`;
    fotoAnunciante.hidden = false;
  } else {
    fotoAnunciante.hidden = true;
  }
  renderizarContatos(advertiser.contacts, ad.title);

  carregando.hidden = true;
  conteudo.hidden = false;
}

await carregar();
