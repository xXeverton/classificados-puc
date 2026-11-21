import { carregarUsuario, sair } from "../fluxos/sessao_atual.js";
import { ROTAS, irPara, mostrarAlerta, montarDependencias } from "./comum.js";

const deps = montarDependencias();
const alerta = document.querySelector("#alerta");
const nome = document.querySelector("#nome-usuario");
const botaoSair = document.querySelector("#sair");

botaoSair.addEventListener("click", async () => {
  botaoSair.disabled = true;
  await sair(deps);
  irPara(ROTAS.entrar);
});

const estado = await carregarUsuario(deps);
if (estado.tipo === "sem_sessao") {
  irPara(ROTAS.entrar, estado.mensagem ? "sessao_expirada" : undefined);
} else if (estado.tipo === "logado") {
  nome.textContent = estado.usuario.nome;
  document.querySelector("#conteudo").hidden = false;
} else {
  mostrarAlerta(alerta, "erro", estado.mensagem);
  document.querySelector("#conteudo").hidden = false;
}
