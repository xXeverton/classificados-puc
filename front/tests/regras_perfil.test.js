import test from "node:test";
import assert from "node:assert/strict";
import {
  normalizarContato,
  textoDoContato,
  validarContato,
  validarFoto,
  validarPerfil,
} from "../js/dominio/regras_perfil.js";
import { MENSAGENS } from "../js/dominio/mensagens.js";

const zap = (valor, codigo_pais = "55") => ({ tipo: "whatsapp", codigo_pais, valor, rotulo: null });
const tel = (valor, codigo_pais = "55") => ({ tipo: "telefone", codigo_pais, valor, rotulo: null });
const simples = (tipo, valor, rotulo = null) => ({ tipo, codigo_pais: null, valor, rotulo });
const ok = (c) => assert.deepEqual(validarContato(c), {});
const erro = (c, campo, mensagem) => assert.equal(validarContato(c)[campo], mensagem);

test("WhatsApp por número: máscara e + são ignorados (CA12)", () => {
  ok(zap("(21) 99999-9999"));
  ok(zap("21999999999", "+55"));
});

test("número: código obrigatório, 8 e 15 dígitos no total aceitos, 7 e 16 recusados (CA15)", () => {
  erro(tel("21999999999", ""), "codigo_pais", MENSAGENS.codigoPaisInvalido);
  erro(zap("21999999999", "5555"), "codigo_pais", MENSAGENS.codigoPaisInvalido);
  ok(tel("999999", "55")); // 2 + 6 = 8
  erro(tel("99999", "55"), "valor", MENSAGENS.numeroTamanho); // 7
  ok(tel("9999999999999", "55")); // 2 + 13 = 15
  erro(tel("99999999999999", "55"), "valor", MENSAGENS.numeroTamanho); // 16
});

test("número com letras ou vazio é recusado (CA15)", () => {
  erro(zap("2199999abcd"), "valor", MENSAGENS.numeroComLetras);
  erro(tel("   "), "valor", MENSAGENS.campoObrigatorio);
});

test("telefone fixo ou celular com país é aceito (CA14)", () => {
  ok(tel("2135271234"));
  ok(tel("21999999999"));
});

test("WhatsApp por link: hosts aceitos (CA13)", () => {
  for (const link of [
    "https://wa.me/5521999999999",
    "https://wa.me/message/ABC123",
    "https://api.whatsapp.com/send?phone=5521999999999",
  ]) ok(zap(link, ""));
});

test("WhatsApp por link: recusa outros hosts e formas enganosas (CA15)", () => {
  for (const link of [
    "http://wa.me/5521999999999",
    "https://example.com/5521999999999",
    "https://wa.me.evil.com/55",
    "https://evil.com/wa.me/55",
    "https://user@wa.me/55",
    "https://wa.me:8080/55",
    "https://wa.me/",
    "https://wa.me",
    "javascript:alert(1)",
  ]) {
    assert.ok(validarContato(zap(link, "")).valor, link);
  }
});

test("e-mail de qualquer domínio; inválido recusado (CA16)", () => {
  ok(simples("email", "ana@gmail.com"));
  ok(simples("email", " Ana@Exemplo.COM "));
  for (const email of ["ana", "ana@", "@gmail.com", "ana@gmail", "a na@x.com"]) {
    erro(simples("email", email), "valor", MENSAGENS.emailContatoInvalido);
  }
});

test("site e link só com https://, sem espaços, sem usuário, com ponto no host (CA17)", () => {
  for (const tipo of ["site", "link"]) {
    ok(simples(tipo, "https://exemplo.com.br/loja?x=1"));
    erro(simples(tipo, "http://exemplo.com"), "valor", MENSAGENS.enderecoSemHttps);
    erro(simples(tipo, "exemplo.com"), "valor", MENSAGENS.enderecoSemHttps);
    erro(simples(tipo, "javascript:alert(1)"), "valor", MENSAGENS.enderecoSemHttps);
    erro(simples(tipo, "https://exem plo.com"), "valor", MENSAGENS.enderecoComEspacos);
    erro(simples(tipo, "https://x@evil.com"), "valor", MENSAGENS.enderecoComUsuario);
    erro(simples(tipo, "https://localhost"), "valor", MENSAGENS.enderecoInvalido);
    erro(simples(tipo, "https://"), "valor", MENSAGENS.enderecoInvalido);
    erro(simples(tipo, `https://exemplo.com/${"a".repeat(2048)}`), "valor", MENSAGENS.enderecoLongo);
  }
});

test("rótulo só em link e até 40 caracteres (CA18)", () => {
  ok(simples("link", "https://instagram.com/ana", "Instagram"));
  ok(simples("link", "https://instagram.com/ana", "a".repeat(40)));
  erro(simples("link", "https://instagram.com/ana", "a".repeat(41)), "rotulo", MENSAGENS.rotuloLongo);
  assert.equal(normalizarContato(simples("link", "https://x.com/a", "  ")).rotulo, null);
  assert.equal(normalizarContato(simples("site", "https://x.com/a", "Loja")).rotulo, null);
});

test("tipo inexistente é recusado (CA11)", () => {
  erro({ tipo: "fax", valor: "1", codigo_pais: null, rotulo: null }, "tipo", MENSAGENS.contatoTipoInvalido);
});

test("normalização: dígitos, minúsculas, pontas, campos que não cabem", () => {
  assert.deepEqual(normalizarContato(zap(" (21) 99999-9999 ", "+55")), {
    tipo: "whatsapp", codigo_pais: "55", valor: "21999999999", rotulo: null,
  });
  assert.deepEqual(normalizarContato(zap(" https://wa.me/55 ", "")), {
    tipo: "whatsapp", codigo_pais: null, valor: "https://wa.me/55", rotulo: null,
  });
  assert.deepEqual(normalizarContato(simples("email", " Ana@X.com ")), {
    tipo: "email", codigo_pais: null, valor: "ana@x.com", rotulo: null,
  });
  assert.equal(normalizarContato({ ...simples("site", "https://x.com"), codigo_pais: "55" }).codigo_pais, null);
});

const contatoValido = simples("email", "ana@x.com");

test("perfil sem nome ou só com espaços (CA7)", () => {
  for (const nome of ["", "   "]) {
    const r = validarPerfil({ nome_exibicao: nome, contatos: [contatoValido], foto: null });
    assert.equal(r.campos.nome_exibicao, MENSAGENS.nomeExibicaoObrigatorio);
    assert.equal(r.valido, false);
  }
});

test("perfil sem contatos (CA8, CA20)", () => {
  const r = validarPerfil({ nome_exibicao: "Ana", contatos: [], foto: null });
  assert.equal(r.campos.contatos, MENSAGENS.nenhumContato);
});

test("limite: 10 contatos aceitos, 11 recusados (CA21)", () => {
  const faz = (n) => Array.from({ length: n }, (_, i) => simples("email", `a${i}@x.com`));
  assert.equal(validarPerfil({ nome_exibicao: "Ana", contatos: faz(10), foto: null }).valido, true);
  const r = validarPerfil({ nome_exibicao: "Ana", contatos: faz(11), foto: null });
  assert.equal(r.campos.contatos, MENSAGENS.limiteDeContatos);
});

test("repetidos recusados; mesmo valor em tipos diferentes e dois links aceitos (CA22, CA19)", () => {
  const repetidos = validarPerfil({
    nome_exibicao: "Ana",
    contatos: [simples("email", "ana@x.com"), simples("email", " ANA@x.com ")],
    foto: null,
  });
  assert.equal(repetidos.valido, false);
  assert.equal(repetidos.campos.contatos, MENSAGENS.contatoRepetido);
  assert.equal(repetidos.contatos[1].valor, MENSAGENS.contatoRepetido);

  const tipos = validarPerfil({
    nome_exibicao: "Ana",
    contatos: [simples("site", "https://x.com/a"), simples("link", "https://x.com/a")],
    foto: null,
  });
  assert.equal(tipos.valido, true);
  const doisLinks = validarPerfil({
    nome_exibicao: "Ana",
    contatos: [simples("link", "https://x.com/a"), simples("link", "https://x.com/b")],
    foto: null,
  });
  assert.equal(doisLinks.valido, true);
});

test("erro de contato indica qual falhou", () => {
  const r = validarPerfil({
    nome_exibicao: "Ana",
    contatos: [contatoValido, simples("site", "http://x.com")],
    foto: null,
  });
  assert.deepEqual(Object.keys(r.contatos), ["1"]);
});

test("foto: formatos e tamanho (CA23, CA24)", () => {
  const arquivo = (type, size) => ({ type, size });
  for (const type of ["image/jpeg", "image/png", "image/webp"]) {
    assert.equal(validarFoto(arquivo(type, 2 * 1024 * 1024)), null);
  }
  assert.equal(validarFoto(null), null);
  assert.equal(validarFoto(arquivo("image/png", 2 * 1024 * 1024 + 1)), MENSAGENS.fotoGrande);
  assert.equal(validarFoto(arquivo("image/gif", 10)), MENSAGENS.fotoFormato);
  assert.equal(validarFoto(arquivo("application/pdf", 10)), MENSAGENS.fotoFormato);
  assert.equal(validarFoto(arquivo("image/png", 0)), MENSAGENS.fotoFormato);
});

test("texto de um contato salvo", () => {
  assert.equal(textoDoContato({ tipo: "whatsapp", codigo_pais: "55", valor: "21999999999", rotulo: null }), "+55 21999999999");
  assert.equal(textoDoContato({ tipo: "link", codigo_pais: null, valor: "https://x.com/a", rotulo: "Instagram" }), "Instagram");
  assert.equal(textoDoContato({ tipo: "email", codigo_pais: null, valor: "a@x.com", rotulo: null }), "a@x.com");
});
