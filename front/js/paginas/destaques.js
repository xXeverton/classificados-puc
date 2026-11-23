// Painel de eventos em destaque do início (spec 015): monta o carrossel só com
// DOM e textContent (D-031). As regras sem DOM ficam em dominio/destaques.js.

import { API_BASE_URL } from "../config.js";
import {
  INTERVALO_CARROSSEL_MS,
  dadosDoDestaque,
  indiceAnterior,
  proximoIndice,
  rotuloDoSlide,
  temCarrossel,
} from "../dominio/destaques.js";
import { resolverUrlRecurso } from "../dominio/detalhes_anuncio.js";
import { criar } from "./comum.js";

function criarSlide(evento, indice, total) {
  const dados = dadosDoDestaque(evento);
  const slide = criar("a", "destaque");
  slide.href = dados.detalhesUrl;
  slide.setAttribute("role", "group");
  slide.setAttribute("aria-roledescription", "slide");
  slide.setAttribute("aria-label", rotuloDoSlide(indice, total));

  if (dados.imagem) {
    const imagem = criar("img", "destaque__imagem");
    imagem.src = resolverUrlRecurso(dados.imagem, API_BASE_URL);
    imagem.alt = "";
    slide.append(imagem);
  } else {
    slide.classList.add("destaque--sem-imagem");
  }

  const texto = criar("div", "destaque__texto");
  texto.append(criar("span", "destaque__selo", "Evento"));
  texto.append(criar("h3", "destaque__titulo", dados.titulo));
  if (dados.data) texto.append(criar("p", "destaque__data", dados.data));
  slide.append(texto);
  return slide;
}

export function criarPainelDeDestaques(secao) {
  const faixa = secao.querySelector("[data-destaques-faixa]");
  const anterior = secao.querySelector("[data-destaques-anterior]");
  const proxima = secao.querySelector("[data-destaques-proxima]");
  const pontos = secao.querySelector("[data-destaques-pontos]");
  const aviso = secao.querySelector("[data-destaques-aviso]");
  const menosMovimento = window.matchMedia("(prefers-reduced-motion: reduce)");

  let slides = [];
  let botoesDePonto = [];
  let atual = 0;
  let timer = null;
  let pausado = false;
  let visivel = false;

  function parar() {
    clearInterval(timer);
    timer = null;
  }

  // Troca sozinho só com 2 ou mais destaques, painel à vista, sem o mouse ou o
  // foco sobre ele e se o aparelho não pediu menos movimento (CA13, CA14).
  function retomar() {
    parar();
    if (!visivel || pausado || menosMovimento.matches) return;
    if (!temCarrossel(slides.length)) return;
    timer = setInterval(
      () => ir(proximoIndice(atual, slides.length), false),
      INTERVALO_CARROSSEL_MS,
    );
  }

  function ir(indice, anunciar) {
    atual = indice;
    slides.forEach((slide, posicao) => { slide.hidden = posicao !== atual; });
    botoesDePonto.forEach((botao, posicao) => {
      if (posicao === atual) botao.setAttribute("aria-current", "true");
      else botao.removeAttribute("aria-current");
    });
    // Só a troca pedida pela pessoa é anunciada; a automática ficaria
    // repetitiva para quem usa leitor de tela.
    if (anunciar) {
      const titulo = slides[atual].querySelector(".destaque__titulo").textContent;
      aviso.textContent = `${rotuloDoSlide(atual, slides.length)}: ${titulo}`;
    }
  }

  function irPelaPessoa(indice) {
    ir(indice, true);
    retomar();
  }

  function renderizar(eventos) {
    parar();
    atual = 0;
    faixa.replaceChildren();
    pontos.replaceChildren();
    aviso.textContent = "";
    slides = eventos.map((evento, indice) => criarSlide(evento, indice, eventos.length));
    faixa.append(...slides);

    const varios = temCarrossel(slides.length);
    anterior.hidden = !varios;
    proxima.hidden = !varios;
    pontos.hidden = !varios;
    botoesDePonto = [];
    if (varios) {
      botoesDePonto = slides.map((_, indice) => {
        const botao = criar("button", "destaques__ponto");
        botao.type = "button";
        botao.setAttribute("aria-label", rotuloDoSlide(indice, slides.length));
        botao.addEventListener("click", () => irPelaPessoa(indice));
        pontos.append(botao);
        return botao;
      });
    }
    if (slides.length) ir(0, false);
    exibir(visivel);
  }

  // `quer` é se o início deve mostrar o painel agora (sem busca nem filtro);
  // ele só aparece de fato se houver destaques (CA17).
  function exibir(quer) {
    visivel = quer && slides.length > 0;
    secao.hidden = !visivel;
    retomar();
  }

  anterior.addEventListener("click", () => {
    irPelaPessoa(indiceAnterior(atual, slides.length));
  });
  proxima.addEventListener("click", () => {
    irPelaPessoa(proximoIndice(atual, slides.length));
  });
  // Só o foco do teclado pausa: o foco que fica no botão depois de um clique
  // do mouse não deve travar o carrossel (CA14).
  const focoDoTeclado = () => Boolean(secao.querySelector(":focus-visible"));
  secao.addEventListener("mouseenter", () => { pausado = true; retomar(); });
  secao.addEventListener("mouseleave", () => {
    pausado = focoDoTeclado();
    retomar();
  });
  secao.addEventListener("focusin", () => {
    if (focoDoTeclado()) pausado = true;
    retomar();
  });
  secao.addEventListener("focusout", (evento) => {
    if (secao.contains(evento.relatedTarget)) return;
    pausado = secao.matches(":hover");
    retomar();
  });
  menosMovimento.addEventListener("change", retomar);

  return { renderizar, exibir };
}
