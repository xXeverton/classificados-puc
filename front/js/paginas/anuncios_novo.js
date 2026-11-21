import { exigirPerfilAnunciante } from "../fluxos/exigir_perfil_anunciante.js";
import { ROTAS, irPara, ligarBotaoSair, mostrarAlerta, montarDependencias } from "./comum.js";

const deps = montarDependencias();
const alerta = document.querySelector("#alerta");
const conteudo = document.querySelector("#conteudo");

ligarBotaoSair(document.querySelector("#sair"), deps);

const estado = await exigirPerfilAnunciante(deps);
if (estado.tipo === "sem_sessao") {
  irPara(ROTAS.entrar, estado.mensagem ? "sessao_expirada" : undefined);
} else if (estado.tipo === "completar_perfil") {
  window.location.replace(estado.destino);
} else if (estado.tipo === "segue") {
  conteudo.hidden = false;
} else {
  conteudo.hidden = false;
  mostrarAlerta(alerta, "erro", estado.mensagem);
}
