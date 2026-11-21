import { MENSAGENS } from "../dominio/mensagens.js";
import { CODIGO_PAIS_PADRAO } from "../dominio/codigos_paises.js";
import { chamarApi, erroDoServidor } from "./conexao.js";
import { carregarUsuario } from "./sessao_atual.js";

// Junta o perfil comum (GET /auth/me) e o de anunciante (GET /perfil-anunciante).
// `anunciante` é null enquanto a pessoa não completou o perfil (404).
export async function obterPerfil({ authApi, perfilApi, armazenamentoSessao }) {
  const estado = await carregarUsuario({ authApi, armazenamentoSessao });
  if (estado.tipo !== "logado") return estado;

  const { resposta, falha } = await chamarApi(() => perfilApi.obter());
  if (falha) return falha;

  if (resposta.status === 200) {
    return { tipo: "perfil", usuario: estado.usuario, anunciante: resposta.corpo };
  }
  if (resposta.status === 404) {
    return { tipo: "perfil", usuario: estado.usuario, anunciante: null };
  }
  if (resposta.status === 401) {
    armazenamentoSessao.apagar();
    return { tipo: "sem_sessao", mensagem: MENSAGENS.sessaoExpirada };
  }
  return erroDoServidor(resposta);
}

// Dados iniciais do formulário. Quem já é anunciante vê os dados atuais, na
// ordem salva (CA5); quem não é parte do perfil comum: nome da conta e um
// contato com o e-mail institucional (CA4).
export function formularioInicial({ usuario, anunciante }) {
  if (anunciante) {
    return {
      nome_exibicao: anunciante.nome_exibicao,
      foto_url: anunciante.foto_url,
      contatos: anunciante.contatos.map(({ tipo, codigo_pais, valor, rotulo }) => ({
        tipo,
        codigo_pais,
        valor,
        rotulo,
      })),
    };
  }
  return {
    nome_exibicao: usuario.nome,
    foto_url: null,
    contatos: [{ tipo: "email", codigo_pais: null, valor: usuario.email, rotulo: null }],
  };
}

// Valores iniciais de um contato novo, por tipo (WhatsApp e telefone começam
// com o Brasil; WhatsApp pode trocar para link na tela).
export function contatoNovo(tipo) {
  const comPais = tipo === "whatsapp" || tipo === "telefone";
  return {
    tipo,
    codigo_pais: comPais ? CODIGO_PAIS_PADRAO : null,
    valor: "",
    rotulo: null,
  };
}
