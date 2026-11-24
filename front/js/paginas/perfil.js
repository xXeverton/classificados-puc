import { obterPerfil } from "../fluxos/obter_perfil.js";
import { criarCarregadorDeFoto } from "../fluxos/carregar_foto.js";
import { MENSAGENS } from "../dominio/mensagens.js";
import { criarListaDeContatos } from "./contatos_visao.js";
import { montarCabecalho } from "./cabecalho.js";
import { ROTAS, irPara, mostrarAlerta, montarDependencias } from "./comum.js";

const VINCULOS = { aluno: "Aluno", funcionario: "Funcionário" };

const deps = montarDependencias();
const alerta = document.querySelector("#alerta");
const conteudo = document.querySelector("#conteudo");
const carregadorDeFoto = criarCarregadorDeFoto(deps);
const texto = (id, valor) => { document.querySelector(id).textContent = valor; };

montarCabecalho(deps);
window.addEventListener("pagehide", () => carregadorDeFoto.revogar());

function mostrarConta(usuario) {
  texto("#conta-nome", usuario.nome);
  texto("#conta-email", usuario.email);
  texto("#conta-nome-usuario", usuario.nome_usuario);
  texto("#conta-vinculo", VINCULOS[usuario.vinculo] ?? usuario.vinculo);
  const temMatricula = Boolean(usuario.matricula);
  document.querySelector("#rotulo-matricula").hidden = !temMatricula;
  document.querySelector("#conta-matricula").hidden = !temMatricula;
  texto("#conta-matricula", usuario.matricula ?? "");
  document.querySelector("#secao-conta").hidden = false;
}

async function mostrarAnunciante(anunciante) {
  document.querySelector("#secao-anunciante").hidden = false;
  document.querySelector("#sem-anunciante").hidden = anunciante !== null;
  document.querySelector("#com-anunciante").hidden = anunciante === null;
  if (anunciante === null) return;

  texto("#anunciante-nome", anunciante.nome_exibicao);
  document.querySelector("#anunciante-contatos").replaceChildren(
    ...criarListaDeContatos(anunciante.contatos)
  );
  const url = await carregadorDeFoto.carregar(anunciante.foto_url);
  if (url) {
    const foto = document.querySelector("#anunciante-foto");
    foto.src = url;
    foto.hidden = false;
    document.querySelector("#anunciante-foto-vazia").hidden = true;
  }
}

const estado = await obterPerfil(deps);
if (estado.tipo === "sem_sessao") {
  irPara(ROTAS.entrar, estado.mensagem ? "sessao_expirada" : undefined);
} else {
  conteudo.hidden = false;
  if (estado.tipo === "perfil") {
    if (new URLSearchParams(window.location.search).get("aviso") === "perfil_salvo") {
      mostrarAlerta(alerta, "sucesso", MENSAGENS.perfilSalvo);
    }
    mostrarConta(estado.usuario);
    await mostrarAnunciante(estado.anunciante);
  } else {
    mostrarAlerta(alerta, "erro", estado.mensagem);
  }
}
