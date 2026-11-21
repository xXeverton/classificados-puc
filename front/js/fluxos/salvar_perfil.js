import { MENSAGENS } from "../dominio/mensagens.js";
import { normalizarContato, validarPerfil } from "../dominio/regras_perfil.js";
import { chamarApi, erroDoServidor } from "./conexao.js";

export const DESTINO_PADRAO = "/perfil/";
// Só estes valores de `?depois=` são aceitos; o resto é ignorado (sem open redirect).
export const DESTINOS_DEPOIS = { anunciar: "/anuncios/novo/" };

export function destinoAposSalvar(depois) {
  return typeof depois === "string" && Object.hasOwn(DESTINOS_DEPOIS, depois)
    ? DESTINOS_DEPOIS[depois]
    : DESTINO_PADRAO;
}

// dados: { nome_exibicao, contatos, foto: File|null, remover_foto: boolean }
export async function salvarPerfil({ perfilApi, armazenamentoSessao }, dados, depois) {
  const validacao = validarPerfil(dados);
  if (!validacao.valido) return { tipo: "validacao", erros: validacao };

  const formulario = new FormData();
  formulario.append("nome_exibicao", dados.nome_exibicao.trim());
  formulario.append("contatos", JSON.stringify(dados.contatos.map(normalizarContato)));
  if (dados.foto) {
    formulario.append("foto", dados.foto, dados.foto.name ?? "foto");
  } else if (dados.remover_foto) {
    formulario.append("remover_foto", "true");
  }

  const { resposta, falha } = await chamarApi(() => perfilApi.salvar(formulario));
  if (falha) return falha;

  if (resposta.status === 200) {
    return {
      tipo: "sucesso",
      anunciante: resposta.corpo,
      destino: destinoAposSalvar(depois),
    };
  }
  if (resposta.status === 400) {
    const mensagem = resposta.corpo?.message ?? MENSAGENS.erroInesperado;
    return {
      tipo: "dados_invalidos",
      mensagem,
      campo: resposta.corpo?.code === "foto_invalida" ? "foto" : null,
    };
  }
  if (resposta.status === 413) {
    return {
      tipo: "arquivo_grande",
      mensagem: resposta.corpo?.message ?? MENSAGENS.fotoGrande,
    };
  }
  if (resposta.status === 401) {
    armazenamentoSessao.apagar();
    return { tipo: "sem_sessao", mensagem: MENSAGENS.sessaoExpirada };
  }
  return erroDoServidor(resposta);
}
