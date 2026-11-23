import { API_BASE_URL } from "../config.js";
import { resolverUrlRecurso } from "../dominio/detalhes_anuncio.js";
import {
  contarCaracteres,
  montarPayloadAnuncio,
  validarAnuncio,
} from "../dominio/anuncio.js";
import { exigirPerfilAnunciante } from "../fluxos/exigir_perfil_anunciante.js";
import { publicarAnuncio } from "../fluxos/publicar_anuncio.js";
import {
  carregarAnuncioParaEdicao as buscarAnuncioParaEdicao,
  mapearAnuncioParaFormulario,
} from "../fluxos/anuncio_edicao.js";
import { chamarApi } from "../fluxos/conexao.js";
import { montarCabecalho } from "./cabecalho.js";
import {
  ROTAS,
  aoEnviar,
  irPara,
  
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
const adEditandoId = new URLSearchParams(window.location.search).get("editar");

montarCabecalho(deps);

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
  let estado;
  if (adEditandoId) {
    const { resposta, falha } = await chamarApi(
      () => deps.adsApi.editar(Number(adEditandoId), payload),
    );
    if (falha) {
      estado = { tipo: "erro", mensagem: "Não foi possível conectar ao servidor." };
    } else if (resposta.status === 200) {
      estado = { tipo: "editado" };
    } else if (resposta.status === 401) {
      estado = { tipo: "sem_sessao" };
    } else if (resposta.status === 422) {
      estado = {
        tipo: "dados_invalidos",
        campos: resposta.corpo?.campos ?? {},
        temCampoDesconhecido: Boolean(resposta.corpo?.campos),
        mensagem: resposta.corpo?.message,
      };
    } else {
      estado = {
        tipo: "erro",
        mensagem: resposta.corpo?.message ?? "Não foi possível salvar o anúncio.",
      };
    }
  } else {
    estado = await publicarAnuncio(deps, criarCorpo(payload));
  }
  if (estado.tipo === "publicado") {
    limparFormularioPublicado();
    irPara(ROTAS.inicio);
  } else if (estado.tipo === "editado") {
    irPara(ROTAS.meusAnuncios);
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

async function carregarAnuncioParaEdicao() {
  if (!adEditandoId) return true;
  document.querySelector("#titulo-pagina").textContent = "Editar anúncio";
  botaoPublicar.textContent = "Salvar alterações";
  const resultado = await buscarAnuncioParaEdicao(deps, adEditandoId);
  if (resultado.tipo !== "carregado") return false;

  const valores = mapearAnuncioParaFormulario(resultado.anuncio);
  titulo.value = valores.titulo;
  categoria.value = valores.categoria;
  descricao.value = valores.descricao;
  estadoConservacao.value = valores.estadoConservacao;
  if (valores.precoACombinar) {
    tipoPreco[1].checked = true;
  } else {
    tipoPreco[0].checked = true;
    preco.value = valores.preco;
  }
  atualizarCamposCondicionais();
  atualizarContadores();
  if (valores.imageUrl) {
    previaImagem.src = resolverUrlRecurso(valores.imageUrl, API_BASE_URL);
    previa.hidden = false;
  }
  return true;
}

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
    const carregado = await carregarAnuncioParaEdicao();
    if (!carregado) {
      mostrarAlerta(alerta, "erro", "Não foi possível carregar o anúncio.");
    } else {
      aoEnviar(
        formulario,
        botaoPublicar,
        adEditandoId ? "Salvando..." : "Publicando...",
        enviar,
      );
    }
  }
}
