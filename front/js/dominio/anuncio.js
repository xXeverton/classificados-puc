export const REGRAS_ANUNCIO = Object.freeze({
  categorias: Object.freeze(["produto", "servico", "evento"]),
  estadosConservacao: Object.freeze(["novo", "usado_regular"]),
  tituloMinimo: 5,
  tituloMaximo: 80,
  descricaoMaxima: 500,
  precoMaximoCentavos: 999999999999n,
  fotoMaximaBytes: 5 * 1024 * 1024,
  formatosFoto: Object.freeze({
    "image/jpeg": Object.freeze(["jpg", "jpeg"]),
    "image/png": Object.freeze(["png"]),
    "image/webp": Object.freeze(["webp"]),
  }),
});

const MENSAGENS = Object.freeze({
  titulo: "O título deve ter entre 5 e 80 caracteres.",
  categoria: "Escolha uma categoria: produto, serviço ou evento.",
  estado: "Informe o estado de conservação do produto.",
  descricao: "Informe uma descrição de até 500 caracteres.",
  tipoPreco: "Escolha informar o preço ou selecionar 'A combinar'.",
  precoVazio: "Informe o preço ou escolha 'A combinar'.",
  precoInvalido:
    "Informe um valor válido, de 0 a 9.999.999.999,99, com até duas casas decimais.",
  fotoFormato: "Formato não permitido. Use JPG, PNG ou WebP.",
  fotoGrande: "A foto excede 5 MB.",
  fotoVazia: "A foto está vazia.",
});

const CAMPOS_PUBLICACAO = new Set([
  "titulo",
  "categoria",
  "estado_conservacao",
  "descricao",
  "tipo_preco",
  "preco",
  "preco_a_combinar",
  "imagem",
]);

export function contarCaracteres(texto) {
  return Array.from(texto.trim()).length;
}

export function normalizarPreco(texto) {
  if (typeof texto !== "string") return null;
  const correspondencia = /^(\d+)(?:[,.](\d{1,2}))?$/.exec(texto.trim());
  if (!correspondencia) return null;

  const inteiro = correspondencia[1].replace(/^0+(?=\d)/, "");
  if (inteiro.length > 10) return null;
  const centavos = (correspondencia[2] ?? "").padEnd(2, "0");
  const valorEmCentavos =
    BigInt(inteiro) * 100n + BigInt(centavos || "0");
  if (valorEmCentavos > REGRAS_ANUNCIO.precoMaximoCentavos) return null;

  return `${inteiro}.${centavos || "00"}`;
}

export function validarFoto(arquivo) {
  if (!arquivo) return null;
  if (arquivo.size === 0) {
    return mensagemComNome(arquivo.name, MENSAGENS.fotoVazia);
  }
  if (arquivo.size > REGRAS_ANUNCIO.fotoMaximaBytes) {
    return mensagemComNome(arquivo.name, MENSAGENS.fotoGrande);
  }

  let tipo = arquivo.type.toLowerCase();
  if (!tipo) {
    const extensao = arquivo.name.split(".").at(-1)?.toLowerCase();
    tipo = Object.entries(REGRAS_ANUNCIO.formatosFoto)
      .find(([, extensoes]) => extensoes.includes(extensao))?.[0] ?? "";
  }
  if (!Object.hasOwn(REGRAS_ANUNCIO.formatosFoto, tipo)) {
    return mensagemComNome(arquivo.name, MENSAGENS.fotoFormato);
  }
  return null;
}

export function validarAnuncio(dados) {
  const titulo = textoAparado(dados.titulo);
  const descricao = textoAparado(dados.descricao);
  const erros = {};

  const tamanhoTitulo = contarCaracteres(titulo);
  if (
    tamanhoTitulo < REGRAS_ANUNCIO.tituloMinimo
    || tamanhoTitulo > REGRAS_ANUNCIO.tituloMaximo
  ) {
    erros.titulo = MENSAGENS.titulo;
  }
  if (!REGRAS_ANUNCIO.categorias.includes(dados.categoria)) {
    erros.categoria = MENSAGENS.categoria;
  }
  if (
    dados.categoria === "produto"
    && !REGRAS_ANUNCIO.estadosConservacao.includes(
      dados.estado_conservacao,
    )
  ) {
    erros.estado_conservacao = MENSAGENS.estado;
  }
  const tamanhoDescricao = contarCaracteres(descricao);
  if (!descricao || tamanhoDescricao > REGRAS_ANUNCIO.descricaoMaxima) {
    erros.descricao = MENSAGENS.descricao;
  }

  const tipoPrecoValido = ["informar", "combinar"].includes(dados.tipo_preco);
  if (!tipoPrecoValido) erros.tipo_preco = MENSAGENS.tipoPreco;

  let precoNormalizado = null;
  if (dados.tipo_preco !== "combinar") {
    if (!textoAparado(dados.preco)) {
      erros.preco = MENSAGENS.precoVazio;
    } else {
      precoNormalizado = normalizarPreco(dados.preco);
      if (precoNormalizado === null) {
        erros.preco = MENSAGENS.precoInvalido;
      }
    }
  }

  const erroFoto = validarFoto(dados.imagem);
  if (erroFoto) erros.imagem = erroFoto;

  return { erros, precoNormalizado };
}

export function montarPayloadAnuncio(dados) {
  const precoACombinar = dados.tipo_preco === "combinar";
  const payload = {
    titulo: textoAparado(dados.titulo),
    categoria: dados.categoria,
    descricao: textoAparado(dados.descricao),
    preco_a_combinar: precoACombinar,
  };

  if (dados.categoria === "produto") {
    payload.estado_conservacao = dados.estado_conservacao;
  }
  if (!precoACombinar) {
    const preco = normalizarPreco(dados.preco);
    if (preco === null) {
      throw new TypeError("O preço precisa ser validado antes do envio.");
    }
    payload.preco = preco;
  }
  return payload;
}

export function mapearErrosPublicacao(campos) {
  const erros = {};
  let temCampoDesconhecido = false;
  for (const [campo, mensagem] of Object.entries(campos)) {
    const destino = campo === "preco_a_combinar" ? "tipo_preco" : campo;
    if (CAMPOS_PUBLICACAO.has(destino)) {
      erros[destino] = mensagem;
    } else {
      temCampoDesconhecido = true;
    }
  }
  return { erros, temCampoDesconhecido };
}

function textoAparado(valor) {
  return typeof valor === "string" ? valor.trim() : "";
}

function mensagemComNome(nome, mensagem) {
  return nome ? `${nome}: ${mensagem}` : mensagem;
}
