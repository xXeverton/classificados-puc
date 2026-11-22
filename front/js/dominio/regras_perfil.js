// Regras do perfil de anunciante para aviso imediato na tela. São as mesmas do
// core; o backend continua sendo a validação definitiva (RN8).

import { MENSAGENS } from "./mensagens.js";

export const TIPOS_DE_CONTATO = ["whatsapp", "email", "telefone", "site", "link"];
export const ROTULOS_DE_TIPO = {
  whatsapp: "WhatsApp",
  email: "E-mail",
  telefone: "Telefone",
  site: "Site",
  link: "Link",
};
export const MAXIMO_CONTATOS = 10;
export const MAXIMO_CARACTERES_ROTULO = 40;
export const MAXIMO_CARACTERES_ENDERECO = 2048;
export const MINIMO_DIGITOS = 8;
export const MAXIMO_DIGITOS = 15;
export const TAMANHO_MAXIMO_FOTO_BYTES = 2 * 1024 * 1024;
export const FORMATOS_DE_FOTO = ["image/jpeg", "image/png", "image/webp"];
export const HOSTS_LINK_WHATSAPP = ["wa.me", "api.whatsapp.com"];

const EMAIL = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
const texto = (valor) => (valor ?? "").trim();
const semMascara = (valor) => texto(valor).replace(/[\s().+-]/g, "");
const semMais = (valor) => texto(valor).replace(/^\+/, "");

function endereco(valor, { whatsapp = false } = {}) {
  const t = texto(valor);
  if (!t) return MENSAGENS.campoObrigatorio;
  if (t.length > MAXIMO_CARACTERES_ENDERECO) return MENSAGENS.enderecoLongo;
  if (/\s/.test(t)) return MENSAGENS.enderecoComEspacos;
  if (!t.toLowerCase().startsWith("https://")) return MENSAGENS.enderecoSemHttps;
  let url;
  try {
    url = new URL(t);
  } catch {
    return MENSAGENS.enderecoInvalido;
  }
  if (url.username || url.password) return MENSAGENS.enderecoComUsuario;
  if (whatsapp) {
    const valido =
      HOSTS_LINK_WHATSAPP.includes(url.hostname) && !url.port && url.pathname.length > 1;
    return valido ? null : MENSAGENS.linkWhatsappInvalido;
  }
  return url.hostname.includes(".") ? null : MENSAGENS.enderecoInvalido;
}

function numero(contato) {
  const erros = {};
  const codigo = semMais(contato.codigo_pais);
  const digitos = semMascara(contato.valor);
  if (!/^\d{1,3}$/.test(codigo)) erros.codigo_pais = MENSAGENS.codigoPaisInvalido;
  if (!digitos) {
    erros.valor = MENSAGENS.campoObrigatorio;
  } else if (!/^\d+$/.test(digitos)) {
    erros.valor = MENSAGENS.numeroComLetras;
  } else if (!erros.codigo_pais) {
    const total = codigo.length + digitos.length;
    if (total < MINIMO_DIGITOS || total > MAXIMO_DIGITOS) erros.valor = MENSAGENS.numeroTamanho;
  }
  return erros;
}

// WhatsApp por número tem código do país; sem código é por link.
const whatsappPorNumero = (c) => texto(c.codigo_pais) !== "";
const porNumero = (c) => c.tipo === "telefone" || (c.tipo === "whatsapp" && whatsappPorNumero(c));

// Erros de um contato, por campo ({} se válido).
export function validarContato(contato) {
  if (!TIPOS_DE_CONTATO.includes(contato.tipo)) {
    return { tipo: MENSAGENS.contatoTipoInvalido };
  }
  const erros = {};
  const { tipo } = contato;
  if (porNumero(contato)) {
    Object.assign(erros, numero(contato));
  } else if (tipo === "whatsapp") {
    const erro = endereco(contato.valor, { whatsapp: true });
    if (erro) erros.valor = erro;
  } else if (tipo === "email") {
    const email = texto(contato.valor);
    if (!email) erros.valor = MENSAGENS.campoObrigatorio;
    else if (!EMAIL.test(email)) erros.valor = MENSAGENS.emailContatoInvalido;
  } else {
    const erro = endereco(contato.valor);
    if (erro) erros.valor = erro;
  }
  if (tipo === "link" && texto(contato.rotulo).length > MAXIMO_CARACTERES_ROTULO) {
    erros.rotulo = MENSAGENS.rotuloLongo;
  }
  return erros;
}

// Forma enviada ao servidor: números só com dígitos, e-mail em minúsculas,
// espaços das pontas removidos, campos que não cabem no tipo nulos.
export function normalizarContato(contato) {
  const { tipo } = contato;
  const rotulo = tipo === "link" ? texto(contato.rotulo) || null : null;
  if (porNumero(contato)) {
    return {
      tipo,
      codigo_pais: semMais(contato.codigo_pais),
      valor: semMascara(contato.valor),
      rotulo,
    };
  }
  const valor = tipo === "email" ? texto(contato.valor).toLowerCase() : texto(contato.valor);
  return { tipo, codigo_pais: null, valor, rotulo };
}

export function validarFoto(arquivo) {
  if (!arquivo) return null;
  if (!FORMATOS_DE_FOTO.includes(arquivo.type) || arquivo.size === 0) {
    return MENSAGENS.fotoFormato;
  }
  if (arquivo.size > TAMANHO_MAXIMO_FOTO_BYTES) return MENSAGENS.fotoGrande;
  return null;
}

// Devolve { campos: {nome_exibicao, contatos, foto}, contatos: {indice: {campo: msg}},
// valido }. O índice é a posição na lista, na ordem em que a pessoa a montou.
export function validarPerfil({ nome_exibicao, contatos, foto }) {
  const campos = {};
  const porContato = {};
  if (!texto(nome_exibicao)) campos.nome_exibicao = MENSAGENS.nomeExibicaoObrigatorio;
  if (contatos.length === 0) campos.contatos = MENSAGENS.nenhumContato;
  else if (contatos.length > MAXIMO_CONTATOS) campos.contatos = MENSAGENS.limiteDeContatos;

  const vistos = new Set();
  contatos.forEach((contato, indice) => {
    const erros = validarContato(contato);
    if (Object.keys(erros).length === 0) {
      const n = normalizarContato(contato);
      const chave = `${n.tipo}|${n.codigo_pais ?? ""}|${n.valor}`;
      if (vistos.has(chave)) {
        erros.valor = MENSAGENS.contatoRepetido;
        campos.contatos ??= MENSAGENS.contatoRepetido;
      }
      vistos.add(chave);
    }
    if (Object.keys(erros).length > 0) porContato[indice] = erros;
  });

  const erroFoto = validarFoto(foto);
  if (erroFoto) campos.foto = erroFoto;
  const valido = Object.keys(campos).length === 0 && Object.keys(porContato).length === 0;
  return { campos, contatos: porContato, valido };
}

// Texto curto de um contato já salvo (resposta da API), para listas.
export function textoDoContato(contato) {
  if (contato.codigo_pais) return `+${contato.codigo_pais} ${contato.valor}`;
  if (contato.tipo === "link" && contato.rotulo) return contato.rotulo;
  return contato.valor;
}
