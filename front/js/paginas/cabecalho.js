// Monta o cabeçalho único das telas com login (D-035). Só createElement e
// textContent (D-031). O que a tela já tiver dentro de `.cabecalho__conteudo`
// (como a busca e os filtros do início) fica entre o logo e o menu.

import {
  BOTAO_NOVO_ANUNCIO,
  ITENS_DO_CABECALHO,
  itemAtual,
} from "../dominio/navegacao.js";
import { ROTAS } from "../dominio/rotas.js";
import { criar, ligarBotaoSair } from "./comum.js";

function criarLink(classe, item, atual) {
  const link = criar("a", classe, item.rotulo);
  link.href = item.rota;
  if (item.chave === atual) link.setAttribute("aria-current", "page");
  return link;
}

function criarMarca() {
  const marca = criar("a", "marca");
  marca.href = ROTAS.inicio;
  marca.append(
    criar("span", "marca__sigla", "PUC"),
    criar("span", "marca__nome", "Classificados"),
  );
  return marca;
}

function criarMenu(atual) {
  const menu = criar("nav", "navegacao");
  menu.setAttribute("aria-label", "Principal");
  for (const item of ITENS_DO_CABECALHO) {
    menu.append(criarLink("navegacao__item", item, atual));
  }
  return menu;
}

export function montarCabecalho(deps) {
  const cabecalho = document.querySelector("[data-cabecalho]");
  let conteudo = cabecalho.querySelector(".cabecalho__conteudo");
  if (!conteudo) {
    conteudo = criar("div", "container cabecalho__conteudo");
    cabecalho.append(conteudo);
  }
  const atual = itemAtual(window.location.pathname, window.location.search);
  const sair = criar("button", "botao botao--contorno", "Sair");
  sair.type = "button";
  sair.id = "sair";

  conteudo.prepend(criarMarca());
  conteudo.append(
    criarMenu(atual),
    criarLink("botao botao--primario", BOTAO_NOVO_ANUNCIO, atual),
    sair,
  );
  ligarBotaoSair(sair, deps);
}
