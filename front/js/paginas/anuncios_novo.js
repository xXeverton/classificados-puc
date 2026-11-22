import {
  contarCaracteres,
  montarPayloadAnuncio,
  validarAnuncio,
} from "../dominio/anuncio.js";
import { exigirPerfilAnunciante } from "../fluxos/exigir_perfil_anunciante.js";
import { publicarAnuncio } from "../fluxos/publicar_anuncio.js";
import {
  ROTAS,
  aoEnviar,
  irPara,
  ligarBotaoSair,
  limparAlerta,
  limparErroDeCampo,
  limparErros,
  mostrarAlerta,
  mostrarErroDeCampo,
  mostrarErrosDeCampo,
  montarDependencias,
} from "./comum.js";

const deps = montarDependencias();
const alerta = document.querySelector("#alerta");
const conteudo = document.querySelector("#conteudo");
const formulario = document.querySelector("#form-anuncio");
const botaoPublicar = document.querySelector("#publicar");
const titulo = formulario.elements.titulo;
const categoria = formulario.elements.categoria;
const campoEstado = document.querySelector("#campo-estado");
const estadoConservacao = formulario.elements.estado_conservacao;
const descricao = formulario.elements.descricao;
const tipoPreco = formulario.elements.tipo_preco;
const campoPreco = document.querySelector("#campo-preco");
const preco = formulario.elements.preco;
const imagem = formulario.elements.imagem;
const previa = document.querySelector("#foto-previa");
const previaImagem = document.querySelector("#foto-previa-imagem");
const removerFoto = document.querySelector("#remover-foto");
let imagemSelecionada = null;
let urlPrevia = null;

ligarBotaoSair(document.querySelector("#sair"), deps);

function coletarDados() {
  return {
    titulo: titulo.value,
    categoria: categoria.value,
    estado_conservacao: estadoConservacao.value,
    descricao: descricao.value,
    tipo_preco: tipoPreco.value,
    preco: preco.value,
    imagem: imagemSelecionada,
  };
}

function atualizarContadores() {
  document.querySelector("#titulo-contador").textContent =
    `${contarCaracteres(titulo.value)}/80`;
  document.querySelector("#descricao-contador").textContent =
    `${contarCaracteres(descricao.value)}/500`;
}

function atualizarCamposCondicionais() {
  const ehProduto = categoria.value === "produto";
  campoEstado.hidden = !ehProduto;
  estadoConservacao.required = ehProduto;
  estadoConservacao.disabled = !ehProduto;
  if (!ehProduto) {
    estadoConservacao.value = "";
    limparErroDeCampo(formulario, "estado_conservacao");
  }

  const combinar = tipoPreco.value === "combinar";
  campoPreco.hidden = combinar;
  preco.disabled = combinar;
  preco.required = !combinar;
  if (combinar) {
    preco.value = "";
    limparErroDeCampo(formulario, "preco");
  }
}

function validarCampo(nome) {
  const { erros } = validarAnuncio(coletarDados());
  if (erros[nome]) {
    mostrarErroDeCampo(formulario, nome, erros[nome]);
  } else {
    limparErroDeCampo(formulario, nome);
  }
}

function ligarValidacaoDeCampo(campo, nome) {
  campo.addEventListener("blur", () => validarCampo(nome));
  campo.addEventListener("input", () => {
    if (campo.hasAttribute("aria-invalid")) validarCampo(nome);
  });
  campo.addEventListener("change", () => {
    if (campo.hasAttribute("aria-invalid")) validarCampo(nome);
  });
}

function liberarPrevia() {
  if (urlPrevia) URL.revokeObjectURL(urlPrevia);
  urlPrevia = null;
  previaImagem.removeAttribute("src");
  previa.hidden = true;
}

function selecionarImagem() {
  imagemSelecionada = imagem.files[0] ?? null;
  const erro = validarAnuncio(coletarDados()).erros.imagem;
  if (erro) {
    liberarPrevia();
    mostrarErroDeCampo(formulario, "imagem", erro);
    return;
  }

  limparErroDeCampo(formulario, "imagem");
  liberarPrevia();
  if (!imagemSelecionada) return;
  urlPrevia = URL.createObjectURL(imagemSelecionada);
  previaImagem.src = urlPrevia;
  previa.hidden = false;
}

function removerImagem() {
  liberarPrevia();
  imagemSelecionada = null;
  imagem.value = "";
  limparErroDeCampo(formulario, "imagem");
  imagem.focus();
}

function criarCorpo(payload) {
  const dados = new FormData();
  for (const [campo, valor] of Object.entries(payload)) {
    dados.set(campo, String(valor));
  }
  if (imagemSelecionada) {
    dados.set("imagem", imagemSelecionada, imagemSelecionada.name);
  }
  return dados;
}

function mostrarPerfilIncompleto(mensagem) {
  mostrarAlerta(alerta, "aviso", `${mensagem} `);
  const link = document.createElement("a");
  link.href = `${ROTAS.editarPerfilAnunciante}?depois=anunciar`;
  link.textContent = "Completar perfil";
  alerta.append(link);
}

function limparFormularioPublicado() {
  liberarPrevia();
  imagemSelecionada = null;
  formulario.reset();
  atualizarCamposCondicionais();
  atualizarContadores();
  limparErros(formulario);
  limparAlerta(alerta);
}

async function enviar() {
  limparErros(formulario);
  limparAlerta(alerta);

  const dados = coletarDados();
  const validacao = validarAnuncio(dados);
  if (Object.keys(validacao.erros).length) {
    mostrarErrosDeCampo(formulario, validacao.erros);
    return;
  }

  const payload = montarPayloadAnuncio(dados);
  const estado = await publicarAnuncio(deps, criarCorpo(payload));
  if (estado.tipo === "publicado") {
    limparFormularioPublicado();
    irPara(ROTAS.inicio);
  } else if (estado.tipo === "sem_sessao") {
    irPara(ROTAS.entrar, "sessao_expirada");
  } else if (estado.tipo === "perfil_incompleto") {
    mostrarPerfilIncompleto(estado.mensagem);
  } else if (estado.tipo === "dados_invalidos") {
    mostrarErrosDeCampo(formulario, estado.campos);
    if (
      estado.temCampoDesconhecido
      || !Object.keys(estado.campos).length
    ) {
      mostrarAlerta(
        alerta,
        "erro",
        estado.mensagem ?? "Não foi possível validar os dados enviados.",
      );
    }
  } else {
    mostrarAlerta(alerta, "erro", estado.mensagem);
  }
}

titulo.addEventListener("input", atualizarContadores);
descricao.addEventListener("input", atualizarContadores);
ligarValidacaoDeCampo(titulo, "titulo");
ligarValidacaoDeCampo(categoria, "categoria");
ligarValidacaoDeCampo(estadoConservacao, "estado_conservacao");
ligarValidacaoDeCampo(descricao, "descricao");
ligarValidacaoDeCampo(preco, "preco");

categoria.addEventListener("change", () => {
  atualizarCamposCondicionais();
  if (categoria.hasAttribute("aria-invalid")) validarCampo("categoria");
});
for (const opcao of tipoPreco) {
  opcao.addEventListener("blur", () => validarCampo("tipo_preco"));
  opcao.addEventListener("change", () => {
    atualizarCamposCondicionais();
    if (tipoPreco[0].hasAttribute("aria-invalid")) {
      validarCampo("tipo_preco");
    }
  });
}
imagem.addEventListener("change", selecionarImagem);
removerFoto.addEventListener("click", removerImagem);
atualizarCamposCondicionais();
atualizarContadores();

const acesso = await exigirPerfilAnunciante(deps);
if (acesso.tipo === "sem_sessao") {
  irPara(ROTAS.entrar, "sessao_expirada");
} else if (acesso.tipo === "completar_perfil") {
  window.location.replace(acesso.destino);
} else {
  conteudo.hidden = false;
  if (acesso.tipo !== "segue") {
    for (const controle of formulario.elements) controle.disabled = true;
    mostrarAlerta(alerta, "erro", acesso.mensagem);
  } else {
    aoEnviar(formulario, botaoPublicar, "Publicando...", enviar);
  }
}
