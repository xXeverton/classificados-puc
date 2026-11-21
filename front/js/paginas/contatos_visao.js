// Lista somente leitura dos contatos de um perfil salvo. Só textContent; os
// endereços vêm validados do servidor, mas só viram link se forem seguros.

import { ROTULOS_DE_TIPO, textoDoContato } from "../dominio/regras_perfil.js";
import { criar } from "./comum.js";

const HREF_SEGURO = /^(https:\/\/|mailto:|tel:\+\d)/;

function enderecoDoContato(contato) {
  let href = null;
  if (contato.tipo === "whatsapp") href = contato.link_de_conversa;
  else if (contato.tipo === "email") href = `mailto:${contato.valor}`;
  else if (contato.tipo === "telefone") href = `tel:+${contato.codigo_pais}${contato.valor}`;
  else href = contato.valor;
  return typeof href === "string" && HREF_SEGURO.test(href) ? href : null;
}

export function criarListaDeContatos(contatos) {
  return contatos.map((contato) => {
    const item = criar("li", "contatos-visao__item");
    item.append(criar("span", "contatos-visao__tipo", ROTULOS_DE_TIPO[contato.tipo] ?? contato.tipo));

    const href = enderecoDoContato(contato);
    const texto = textoDoContato(contato);
    if (href) {
      const link = criar("a", "", texto);
      link.href = href;
      if (href.startsWith("https://")) {
        link.target = "_blank";
        link.rel = "noopener noreferrer";
      }
      item.append(link);
    } else {
      item.append(criar("span", "", texto));
    }
    // Rótulo de link (CA18): o endereço aparece junto, para quem lê saber o destino.
    if (contato.tipo === "link" && contato.rotulo) {
      item.append(criar("span", "contatos-visao__detalhe", contato.valor));
    }
    return item;
  });
}
