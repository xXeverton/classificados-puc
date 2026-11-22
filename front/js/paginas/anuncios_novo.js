import { exigirPerfilAnunciante } from "../fluxos/exigir_perfil_anunciante.js";
import { publicarAnuncio } from "../fluxos/publicar_anuncio.js";
import {
  ROTAS,
  aoEnviar,
  irPara,
  ligarBotaoSair,
  limparErros,
  mostrarAlerta,
  mostrarErrosDeCampo,
  montarDependencias,
} from "./comum.js";

const deps = montarDependencias();
const alerta = document.querySelector("#alerta");
const conteudo = document.querySelector("#conteudo");
const formulario = document.querySelector("#form-anuncio");
const botaoPublicar = document.querySelector("#publicar");
const categoria = formulario.elements.categoria;
const campoEstado = document.querySelector("#campo-estado");
const estadoConservacao = formulario.elements.estado_conservacao;
const precoACombinar = formulario.elements.preco_a_combinar;
const preco = formulario.elements.preco;

ligarBotaoSair(document.querySelector("#sair"), deps);

function atualizarCamposCondicionais() {
  const ehProduto = categoria.value === "produto";
  campoEstado.hidden = !ehProduto;
  estadoConservacao.required = ehProduto;
  estadoConservacao.disabled = !ehProduto;
  if (!ehProduto) estadoConservacao.value = "";

  preco.disabled = precoACombinar.checked;
  preco.required = !precoACombinar.checked;
  if (precoACombinar.checked) preco.value = "";
}

function validar() {
  const erros = {};
  const titulo = formulario.elements.titulo.value.trim();
  const descricao = formulario.elements.descricao.value.trim();
  if (titulo.length < 5 || titulo.length > 80) {
    erros.titulo = "O título deve ter entre 5 e 80 caracteres.";
  }
  if (!categoria.value) erros.categoria = "Escolha uma categoria.";
  if (
    categoria.value === "produto"
    && !["novo", "usado_regular"].includes(estadoConservacao.value)
  ) {
    erros.estado_conservacao = "Informe o estado do produto.";
  }
  if (!descricao || descricao.length > 500) {
    erros.descricao = "Informe uma descrição de até 500 caracteres.";
  }
  if (
    !precoACombinar.checked
    && !/^[0-9]+(?:[,.][0-9]{1,2})?$/.test(preco.value.trim())
  ) {
    erros.preco = "Informe um preço válido ou selecione “A combinar”.";
  }
  const imagem = formulario.elements.imagem.files[0];
  if (
    imagem
    && !["image/jpeg", "image/png", "image/webp"].includes(imagem.type)
  ) {
    erros.imagem = "Use uma imagem JPG, PNG ou WEBP.";
  }
  if (imagem && imagem.size > 5 * 1024 * 1024) {
    erros.imagem = "A imagem deve ter no máximo 5 MiB.";
  }
  return erros;
}

async function enviar() {
  limparErros(formulario);
  const erros = validar();
  if (Object.keys(erros).length) {
    mostrarErrosDeCampo(formulario, erros);
    return;
  }

  const dados = new FormData(formulario);
  if (precoACombinar.checked) {
    dados.set("preco_a_combinar", "true");
    dados.delete("preco");
  }
  const estado = await publicarAnuncio(deps, dados);
  if (estado.tipo === "publicado") {
    irPara(ROTAS.inicio);
  } else if (estado.tipo === "sem_sessao") {
    irPara(ROTAS.entrar, "sessao_expirada");
  } else if (estado.tipo === "completar_perfil") {
    window.location.replace(estado.destino);
  } else if (estado.tipo === "dados_invalidos") {
    mostrarErrosDeCampo(formulario, estado.campos);
    mostrarAlerta(alerta, "erro", estado.mensagem ?? "Dados inválidos.");
  } else {
    mostrarAlerta(alerta, "erro", estado.mensagem);
  }
}

categoria.addEventListener("change", atualizarCamposCondicionais);
precoACombinar.addEventListener("change", atualizarCamposCondicionais);
atualizarCamposCondicionais();

const acesso = await exigirPerfilAnunciante(deps);
if (acesso.tipo === "sem_sessao") {
  irPara(ROTAS.entrar, acesso.mensagem ? "sessao_expirada" : undefined);
} else if (acesso.tipo === "completar_perfil") {
  window.location.replace(acesso.destino);
} else {
  conteudo.hidden = false;
  if (acesso.tipo !== "segue") {
    mostrarAlerta(alerta, "erro", acesso.mensagem);
  } else {
    aoEnviar(formulario, botaoPublicar, "Publicando…", enviar);
  }
}
