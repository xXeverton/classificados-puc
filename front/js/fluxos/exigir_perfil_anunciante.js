import { obterPerfil } from "./obter_perfil.js";

export const DESTINO_COMPLETAR_PERFIL = "/perfil/anunciante/?depois=anunciar";

// Guarda da publicação de anúncios: só segue quem já é anunciante (CA29). Quem
// não é vai completar o perfil e volta depois (CA27, CA28). Falhas de conexão
// ou do servidor não liberam nem redirecionam: a tela mostra o aviso.
export async function exigirPerfilAnunciante(deps) {
  const estado = await obterPerfil(deps);
  if (estado.tipo !== "perfil") return estado;
  if (estado.anunciante === null) {
    return { tipo: "completar_perfil", destino: DESTINO_COMPLETAR_PERFIL };
  }
  return { tipo: "segue", usuario: estado.usuario, anunciante: estado.anunciante };
}
