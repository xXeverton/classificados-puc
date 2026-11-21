import { contatoNovo, formularioInicial, obterPerfil } from "../fluxos/obter_perfil.js";
import { criarCarregadorDeFoto } from "../fluxos/carregar_foto.js";
import { salvarPerfil } from "../fluxos/salvar_perfil.js";
import { CODIGO_PAIS_PADRAO, PAISES, textoDoPais } from "../dominio/codigos_paises.js";
import {
  MAXIMO_CONTATOS,
  ROTULOS_DE_TIPO,
  validarFoto,
} from "../dominio/regras_perfil.js";
import {
  ROTAS,
  aoEnviar,
  criar,
  irPara,
  ligarBotaoSair,
  limparAlerta,
  limparErros,
  mostrarAlerta,
  mostrarErrosDeCampo,
  montarDependencias,
} from "./comum.js";

const VINCULOS = { aluno: "Aluno", funcionario: "Funcionário" };

const deps = montarDependencias();
const depois = new URLSearchParams(window.location.search).get("depois");
const alerta = document.querySelector("#alerta");
const conteudo = document.querySelector("#conteudo");
const formulario = document.querySelector("#form-perfil");
const lista = document.querySelector("#lista-contatos");
const erroDosContatos = document.querySelector("#contatos-erro");
const novoTipo = document.querySelector("#novo-tipo");
const botaoAdicionar = document.querySelector("#adicionar-contato");
const contador = document.querySelector("#contador-contatos");
const campoFoto = document.querySelector("#campo-foto");
const botaoRemoverFoto = document.querySelector("#remover-foto");
const fotoPrevia = document.querySelector("#foto-previa");
const fotoVazia = document.querySelector("#foto-vazia");
const carregadorDeFoto = criarCarregadorDeFoto(deps);

// Estado do formulário. Os campos atualizam estes dados a cada digitação; a
// lista só é redesenhada quando a estrutura muda (adicionar, remover, mover,
// trocar o jeito de informar o WhatsApp), então nada digitado se perde.
let contatos = [];
let proximaChave = 0;
let fotoUrlAtual = null;
let fotoAtualBlob = null;
let fotoNova = null;
let fotoNovaBlob = null;
let removerFoto = false;

ligarBotaoSair(document.querySelector("#sair"), deps);
window.addEventListener("pagehide", () => {
  carregadorDeFoto.revogar();
  revogarPrevia();
});

// ---------------------------------------------------------------- foto

function revogarPrevia() {
  if (fotoNovaBlob) URL.revokeObjectURL(fotoNovaBlob);
  fotoNovaBlob = null;
}

function mostrarFoto() {
  const src = fotoNova ? fotoNovaBlob : removerFoto ? null : fotoAtualBlob;
  const temFoto = Boolean(fotoNova) || (Boolean(fotoUrlAtual) && !removerFoto);
  if (src) fotoPrevia.src = src;
  fotoPrevia.hidden = !src;
  fotoVazia.hidden = Boolean(src);
  fotoVazia.textContent = temFoto ? "Foto atual" : "Sem foto";
  botaoRemoverFoto.hidden = !temFoto;
}

campoFoto.addEventListener("change", () => {
  const arquivo = campoFoto.files[0] ?? null;
  const erro = validarFoto(arquivo);
  limparErros(formulario);
  if (erro || !arquivo) {
    campoFoto.value = "";
    if (erro) mostrarErrosDeCampo(formulario, { foto: erro });
    return;
  }
  revogarPrevia();
  fotoNova = arquivo;
  fotoNovaBlob = URL.createObjectURL(arquivo);
  removerFoto = false;
  mostrarFoto();
});

botaoRemoverFoto.addEventListener("click", () => {
  revogarPrevia();
  fotoNova = null;
  campoFoto.value = "";
  removerFoto = Boolean(fotoUrlAtual);
  mostrarFoto();
  campoFoto.focus();
});

// ------------------------------------------------------------- contatos

const idDoCampo = (c, nome) => `contato-${c.chave}-${nome}`;

function campoDeTexto(c, nome, { rotulo, tipo = "text", opcional = false, ajuda, inputmode }) {
  const id = idDoCampo(c, nome);
  const campo = criar("div", "campo");
  const etiqueta = criar("label", "campo__rotulo", rotulo);
  etiqueta.htmlFor = id;
  if (opcional) etiqueta.append(" ", criar("span", "campo__opcional", "(opcional)"));
  const entrada = criar("input", "campo__entrada");
  Object.assign(entrada, { id, type: tipo, value: c[nome] ?? "", autocomplete: "off" });
  if (inputmode) entrada.inputMode = inputmode;
  entrada.addEventListener("input", () => { c[nome] = entrada.value; });
  campo.append(etiqueta, entrada);
  if (ajuda) campo.append(criar("span", "campo__ajuda", ajuda));
  const erro = criar("span", "campo__erro");
  erro.id = `${id}-erro`;
  campo.append(erro);
  return campo;
}

function campoDePais(c) {
  const id = idDoCampo(c, "codigo_pais");
  const campo = criar("div", "campo");
  const etiqueta = criar("label", "campo__rotulo", "País");
  etiqueta.htmlFor = id;
  const seletor = criar("select", "campo__entrada");
  seletor.id = id;
  const paises = PAISES.some((p) => p.codigo === c.codigo_pais)
    ? PAISES
    : [...PAISES, { nome: "Outro", codigo: c.codigo_pais }];
  for (const pais of paises) {
    const opcao = criar("option", "", textoDoPais(pais));
    opcao.value = pais.codigo;
    seletor.append(opcao);
  }
  seletor.value = c.codigo_pais;
  seletor.addEventListener("change", () => { c.codigo_pais = seletor.value; });
  const erro = criar("span", "campo__erro");
  erro.id = `${id}-erro`;
  campo.append(etiqueta, seletor, erro);
  return campo;
}

function camposDeNumero(c) {
  const grupo = criar("div", "contato__campos contato__campos--dupla");
  grupo.append(
    campoDePais(c),
    campoDeTexto(c, "valor", { rotulo: "Número", tipo: "tel", inputmode: "tel", ajuda: "Só o número, com DDD." })
  );
  return grupo;
}

function modoDoWhatsapp(c) {
  const grupo = criar("fieldset", "campo opcoes");
  grupo.append(criar("legend", "campo__rotulo", "Informar por"));
  for (const [modo, rotulo] of [["numero", "Número"], ["link", "Link"]]) {
    const item = criar("label", "opcoes__item");
    const radio = criar("input");
    Object.assign(radio, {
      type: "radio",
      name: `modo-${c.chave}`,
      value: modo,
      checked: (modo === "numero") === (c.codigo_pais !== null),
    });
    radio.addEventListener("change", () => {
      c.codigo_pais = modo === "numero" ? CODIGO_PAIS_PADRAO : null;
      c.valor = "";
      desenharContatos({ foco: idDoCampo(c, "valor") });
    });
    item.append(radio, ` ${rotulo}`);
    grupo.append(item);
  }
  return grupo;
}

function camposDoContato(c) {
  const grupo = criar("div", "contato__campos");
  if (c.tipo === "whatsapp") {
    grupo.append(modoDoWhatsapp(c));
    grupo.append(
      c.codigo_pais !== null
        ? camposDeNumero(c)
        : campoDeTexto(c, "valor", {
            rotulo: "Link de conversa do WhatsApp",
            tipo: "url",
            inputmode: "url",
            ajuda: "Por exemplo, https://wa.me/5521999999999.",
          })
    );
  } else if (c.tipo === "telefone") {
    grupo.append(camposDeNumero(c));
  } else if (c.tipo === "email") {
    grupo.append(campoDeTexto(c, "valor", { rotulo: "E-mail", tipo: "email", inputmode: "email" }));
  } else if (c.tipo === "site") {
    grupo.append(campoDeTexto(c, "valor", { rotulo: "Endereço do site", tipo: "url", inputmode: "url", ajuda: "Começa com https://." }));
  } else {
    grupo.classList.add("contato__campos--dupla");
    grupo.append(
      campoDeTexto(c, "valor", { rotulo: "Endereço do link", tipo: "url", inputmode: "url", ajuda: "Começa com https://." }),
      campoDeTexto(c, "rotulo", { rotulo: "Rótulo", opcional: true, ajuda: "Por exemplo, Instagram." })
    );
  }
  return grupo;
}

// Ordem atual da lista na tela. A lista de `contatos` é sincronizada a partir
// dela ao soltar; os campos não são redesenhados, então erros e textos ficam.
function sincronizarOrdem() {
  const porChave = new Map(contatos.map((c) => [String(c.chave), c]));
  contatos = [...lista.children].map((item) => porChave.get(item.dataset.chave));
}

function alcaDeArrastar(c, item) {
  const alca = criar("button", "contato__alca");
  alca.type = "button";
  alca.setAttribute(
    "aria-label",
    `Reordenar contato ${ROTULOS_DE_TIPO[c.tipo]}. Arraste, ou use as setas para cima e para baixo.`
  );

  alca.addEventListener("pointerdown", (evento) => {
    if (evento.button !== 0) return;
    evento.preventDefault();
    alca.setPointerCapture(evento.pointerId);
    item.classList.add("contato--arrastando");
  });

  alca.addEventListener("pointermove", (evento) => {
    if (!alca.hasPointerCapture(evento.pointerId)) return;
    const outros = [...lista.children].filter((outro) => outro !== item);
    const alvo = outros.find((outro) => {
      const caixa = outro.getBoundingClientRect();
      return evento.clientY < caixa.top + caixa.height / 2;
    }) ?? null;
    if (alvo !== item.nextElementSibling) lista.insertBefore(item, alvo);
    // Rola a página quando o contato é levado até a borda da tela.
    if (evento.clientY < 60) window.scrollBy(0, -12);
    else if (evento.clientY > window.innerHeight - 60) window.scrollBy(0, 12);
  });

  const soltar = (evento) => {
    if (!alca.hasPointerCapture(evento.pointerId)) return;
    alca.releasePointerCapture(evento.pointerId);
    item.classList.remove("contato--arrastando");
    sincronizarOrdem();
  };
  alca.addEventListener("pointerup", soltar);
  alca.addEventListener("pointercancel", soltar);

  // Teclado: com a alça focada, as setas movem o contato.
  alca.addEventListener("keydown", (evento) => {
    const deslocamento = { ArrowUp: -1, ArrowDown: 1 }[evento.key];
    if (!deslocamento) return;
    evento.preventDefault();
    const vizinho = deslocamento < 0 ? item.previousElementSibling : item.nextElementSibling;
    if (!vizinho) return;
    if (deslocamento < 0) lista.insertBefore(item, vizinho);
    else lista.insertBefore(vizinho, item);
    sincronizarOrdem();
    alca.focus();
  });
  return alca;
}

function itemDoContato(c) {
  const item = criar("li", "contato");
  item.dataset.chave = c.chave;
  const topo = criar("div", "contato__topo");
  topo.append(alcaDeArrastar(c, item), criar("span", "contato__titulo", ROTULOS_DE_TIPO[c.tipo]));
  const remover = criar("button", "botao botao--texto", "Remover");
  remover.type = "button";
  remover.setAttribute("aria-label", `Remover contato ${ROTULOS_DE_TIPO[c.tipo]}`);
  remover.addEventListener("click", () => removerContato(c));
  topo.append(remover);
  item.append(topo, camposDoContato(c));
  return item;
}

function desenharContatos({ foco } = {}) {
  lista.replaceChildren(...contatos.map(itemDoContato));
  contador.textContent = `${contatos.length} de ${MAXIMO_CONTATOS} contatos`;
  botaoAdicionar.disabled = contatos.length >= MAXIMO_CONTATOS;
  erroDosContatos.textContent = "";
  if (foco) document.getElementById(foco)?.focus();
}

function adicionar() {
  if (contatos.length >= MAXIMO_CONTATOS) return;
  const c = { chave: proximaChave++, ...contatoNovo(novoTipo.value) };
  contatos.push(c);
  desenharContatos({ foco: idDoCampo(c, c.tipo === "whatsapp" || c.tipo === "telefone" ? "codigo_pais" : "valor") });
}

function removerContato(c) {
  contatos = contatos.filter((outro) => outro !== c);
  desenharContatos();
  novoTipo.focus();
}

botaoAdicionar.addEventListener("click", adicionar);

// ---------------------------------------------------------------- erros

function mostrarErrosDosContatos(porContato) {
  for (const [indice, erros] of Object.entries(porContato)) {
    const c = contatos[Number(indice)];
    for (const [campo, mensagem] of Object.entries(erros)) {
      const entrada = document.getElementById(idDoCampo(c, campo));
      const erro = document.getElementById(`${idDoCampo(c, campo)}-erro`);
      if (!entrada || !erro) continue;
      erro.textContent = mensagem;
      entrada.setAttribute("aria-invalid", "true");
      entrada.setAttribute("aria-describedby", erro.id);
    }
  }
}

function mostrarErros(erros) {
  const { campos, contatos: porContato } = erros;
  const { contatos: erroGeral, ...deCampo } = campos;
  mostrarErrosDeCampo(formulario, deCampo); // limpa os erros anteriores
  erroDosContatos.textContent = erroGeral ?? "";
  mostrarErrosDosContatos(porContato);
  // Foca o primeiro campo com erro na ordem em que aparecem na tela.
  const primeiro = formulario.querySelector('[aria-invalid="true"]');
  (primeiro ?? (erroGeral ? novoTipo : null))?.focus();
}

// ------------------------------------------------------------- envio

aoEnviar(formulario, formulario.querySelector("button[type=submit]"), "Salvando…", async () => {
  limparAlerta(alerta);
  const estado = await salvarPerfil(
    deps,
    {
      nome_exibicao: formulario.elements.nome_exibicao.value,
      contatos: contatos.map(({ chave: _chave, ...contato }) => contato),
      foto: fotoNova,
      remover_foto: removerFoto,
    },
    depois
  );

  if (estado.tipo === "validacao") {
    mostrarErros(estado.erros);
    return;
  }
  limparErros(formulario);
  erroDosContatos.textContent = "";

  if (estado.tipo === "sucesso") {
    irPara(estado.destino, estado.destino === ROTAS.perfil ? "perfil_salvo" : undefined);
  } else if (estado.tipo === "sem_sessao") {
    irPara(ROTAS.entrar, "sessao_expirada");
  } else if (estado.campo === "foto" || estado.tipo === "arquivo_grande") {
    mostrarErrosDeCampo(formulario, { foto: estado.mensagem });
  } else {
    // Falha de conexão ou do servidor: nada do que foi preenchido é perdido.
    mostrarAlerta(alerta, "erro", estado.mensagem);
  }
});

// -------------------------------------------------------------- início

const estado = await obterPerfil(deps);
if (estado.tipo === "sem_sessao") {
  irPara(ROTAS.entrar, estado.mensagem ? "sessao_expirada" : undefined);
} else {
  conteudo.hidden = false;
  if (estado.tipo === "perfil") {
    const inicial = formularioInicial(estado);
    document.querySelector("#vinculo").textContent =
      VINCULOS[estado.usuario.vinculo] ?? estado.usuario.vinculo;
    formulario.elements.nome_exibicao.value = inicial.nome_exibicao;
    contatos = inicial.contatos.map((c) => ({ chave: proximaChave++, ...c }));
    fotoUrlAtual = inicial.foto_url;
    formulario.hidden = false;
    desenharContatos();
    mostrarFoto();
    fotoAtualBlob = await carregadorDeFoto.carregar(fotoUrlAtual);
    mostrarFoto();
    formulario.elements.nome_exibicao.focus();
  } else {
    mostrarAlerta(alerta, "erro", estado.mensagem);
  }
}
