# Spec: Botões de contato na página do anúncio

- **ID**: 011
- **Status**: Implementada
- **Data**: 2026-11-22
- **Jira**: PROJ-51
- **Decisões gerais aplicadas**: D-004, D-013, D-030, D-032, D-033, D-034,
  D-051
- **Depende de**: PROJ-50 e spec 004-detalhar-anuncio

## História de usuário

**Como** comprador interessado,
**quero** clicar em “Chamar no WhatsApp” ou “Enviar E-mail” na página do
anúncio,
**para que** eu possa negociar diretamente com o anunciante pelo canal que
preferir.

**Como** comprador,
**quero** que os links usem os dados atuais do perfil do vendedor,
**para que** eu não contacte um número ou endereço desatualizado.

**Como** comprador no celular ou no computador,
**quero** que os botões funcionem nos dois tipos de dispositivo,
**para que** eu possa iniciar o contato independentemente de onde estou.

## Critérios de aceitação

- [x] CA1: Dado que estou na página de um anúncio disponível, quando ela
  carregar, então vejo em destaque os botões “Chamar no WhatsApp” e
  “Enviar E-mail”.
- [x] CA2: Dado que clico em “Chamar no WhatsApp”, quando o contato estiver
  disponível, então sou levado ao WhatsApp em nova aba ou janela com a
  mensagem “Olá! Vi seu anúncio {Título} no PUC pra Rolo e tenho interesse.”
  preenchida pelo utilitário da feature PROJ-50.
- [x] CA3: Dado que clico em “Enviar E-mail”, quando o contato estiver
  disponível, então o aplicativo de e-mail abre em nova aba ou janela com o
  endereço do vendedor no destinatário.
- [x] CA4: O e-mail aberto pelo botão deve usar como assunto
  “Interesse no anúncio: {Título}” e como corpo
  “Olá! Tenho interesse no anúncio {Título} no PUC pra Rolo.”.
- [x] CA5: Dado que o vendedor alterou o número ou e-mail no perfil, quando um
  comprador abrir o anúncio novamente, então os botões usam os contatos atuais
  retornados pela página do anúncio.
- [x] CA6: Dado um título com acentos, emojis ou símbolos, quando o comprador
  usa qualquer botão, então o título chega íntegro à mensagem ou ao e-mail.
- [x] CA7: Dado que acesso pelo celular ou computador, quando ativo um dos
  botões, então o link abre o aplicativo ou canal correspondente sem quebrar o
  funcionamento da página.
- [x] CA8: Dado que não estou autenticado, quando tento abrir a página do
  anúncio, então a plataforma exige login e não permite visualizar ou ativar os
  contatos.

## Regras de negócio

- RN1: Esta feature reaproveita os contatos atuais do perfil do anunciante
  fornecidos pela página detalhada (D-013). Não busca nem mantém cópia
  desatualizada desses dados.
- RN2: O botão “Chamar no WhatsApp” usa o utilitário aprovado pela PROJ-50
  para montar o link e a mensagem inicial.
- RN3: O botão “Enviar E-mail” usa um endereço `mailto:` com destinatário,
  assunto e corpo codificados para URL.
- RN4: Os links externos usam `target="_blank"` e uma relação segura para evitar
  associação da nova aba com a página atual.
- RN5: Todo conteúdo da página exige conta autenticada e confirmada (D-004).
- RN6: Os títulos são tratados como texto e nunca interpretados como HTML
  (D-031).
- RN7: O botão não deve iniciar chat interno, pagamento ou fluxo de
  intermediação financeira.

## Mensagens e rótulos

- WhatsApp: `Chamar no WhatsApp`.
- E-mail: `Enviar E-mail`.
- Assunto do e-mail: `Interesse no anúncio: {Título}`.
- Corpo do e-mail:
  `Olá! Tenho interesse no anúncio {Título} no PUC pra Rolo.`.

## Fora de escopo

- Geração ou normalização do link do WhatsApp, definida pela PROJ-50.
- Comportamento visual ou decisão funcional quando falta WhatsApp ou e-mail,
  definida pela PROJ-52.
- Editar perfil ou contatos do vendedor.
- Chat interno, reserva, pagamento ou intermediação financeira.
- Mudança da página para acesso anônimo.

## Dúvidas em aberto

Nenhuma dúvida pendente.
