# Plano técnico: Botões de contato na página do anúncio

Referência: `spec.md` desta pasta.

Dependências:

- `D-004` exige sessão autenticada e confirmada para a página.
- `D-013` fornece os contatos atuais do anunciante.
- `D-030` exige HTML, CSS e JavaScript puros, sem framework ou dependências.
- `D-034` exige os componentes existentes do tema e do guia de estilo.
- PROJ-50 fornece o utilitário puro de geração do link do WhatsApp.
- PROJ-52 define separadamente o que acontece quando um contato está ausente.

## Domínio (`front/js/dominio/`)

- Reutilizar o utilitário `gerarLinkWhatsapp` de PROJ-50.
- Criar apenas transformações necessárias para montar o endereço `mailto:`,
  incluindo destinatário, assunto e corpo codificados.
- Não armazenar número, e-mail ou título em estado global.
- Não decidir ausência ou fallback de contatos nesta feature.
- Centralizar os rótulos e templates de assunto/corpo sem espalhar strings
  soltas pela camada da página.

## Página existente (`front/anuncios/detalhes/`)

- Alterar `detalhes_anuncio.js` para renderizar os contatos prioritários com
  os rótulos definidos pela spec.
- Reutilizar o bloco `#contatos` já existente.
- Separar a construção dos links da renderização visual.
- Abrir os links externos em nova aba/janela, com `target="_blank"` e
  `rel="noopener noreferrer"`.
- Preservar o comportamento dos demais contatos já cadastrados.
- Usar `textContent` e componentes existentes; não usar `innerHTML`.

## Contratos

O contrato da página continua recebendo da API o anunciante e sua lista atual
de contatos. Os dados relevantes permanecem:

- contato do tipo `whatsapp`: número ou link já cadastrado.
- contato do tipo `email`: endereço válido.
- anúncio: título atual usado nas mensagens.

O utilitário de WhatsApp recebe o número do contato e o título do anúncio. O
`mailto:` recebe o e-mail, assunto e corpo gerados a partir do título.

## Interface web

- Nenhuma rota ou endpoint novo é necessário.
- Nenhuma alteração em banco de dados ou persistência é necessária.
- A página detalhada já exige sessão conforme a spec 004.
- Links externos não são enviados ao servidor.

## Princípios SOLID aplicados

- O domínio mantém funções pequenas e puras para formatação dos links.
- A página apenas transforma dados da API em elementos visuais e usa os
  módulos puros.
- Nenhuma função da camada da página acessa armazenamento ou estado global
  além das dependências já existentes da tela.

## Estrutura de testes

- Testes unitários em `front/tests/detalhes.test.js` ou em módulo de domínio
  específico para:
  - rótulos dos dois contatos;
  - link do WhatsApp com mensagem pré-preenchida;
  - link de e-mail com destinatário, assunto e corpo;
  - codificação de título com acentos e símbolos;
  - abertura em nova aba;
  - uso de contato novo em chamadas sucessivas.
- Testes manuais da página em celular e computador, quando aplicável.
- `make front-test` deve continuar passando.
- Nenhum teste de backend, banco ou flake8 é necessário para esta mudança
  restrita ao front-end.
