# Spec: Utilitário para gerar link de contato do WhatsApp

- **ID**: 010
- **Status**: Rascunho
- **Data**: 2026-11-22
- **Jira**: PROJ-50
- **Decisões gerais aplicadas**: D-013, D-030, D-051
- **Relacionadas**: PROJ-51 (interface consumidora) e PROJ-52 (fallback de
  exibição)

## História de usuário

**Como** desenvolvedor da interface,
**quero** gerar um link de WhatsApp a partir do número atual do anunciante e do
título do anúncio,
**para que** o comprador possa iniciar uma conversa com uma mensagem
preenchida.

**Como** comprador,
**quero** abrir o WhatsApp com uma mensagem sobre o anúncio,
**para que** eu não precise digitá-la.

## Critérios de aceitação

- [ ] CA1: Dado um número brasileiro com máscara, quando o link é solicitado,
  então o número é normalizado para dígitos, recebe o código 55 se ausente e
  não recebe um segundo código 55 se já estiver presente.
- [ ] CA2: Dado um número brasileiro ausente ou inválido, quando o link é
  solicitado, então o utilitário indica que não há link disponível sem lançar
  uma exceção que interrompa a página.
- [ ] CA3: Dado um número válido e um título, quando o link é gerado, então ele
  segue o formato `https://wa.me/{numero}?text={mensagem}`.
- [ ] CA4: Dado um título com acentos, espaços, emojis ou caracteres especiais,
  quando o link é gerado, então a mensagem é codificada para URL e o conteúdo
  chega íntegro ao WhatsApp.
- [ ] CA5: **Pendente de confirmação do PO:** dado um número válido e o título
  "Bicicleta Caloi", quando o link é gerado, então a mensagem proposta é
  "Olá! Vi seu anúncio Bicicleta Caloi no PUC pra Rolo e tenho interesse."
- [ ] CA6: Dado que o perfil atual do anunciante fornece o número, quando o
  utilitário é chamado, então o link usa o número recebido e não um número
  fixo ou uma cópia previamente armazenada.

## Regras de negócio

- RN1: O número de WhatsApp vem do contato do perfil do anunciante
  (D-013). O perfil mantém `codigo_pais` separado de `valor`; números são
  representados em `valor` sem máscara, e o código do país é informado
  separadamente. Para esta função, o chamador fornece o número como uma única
  string, combinando o código do país (quando presente) e `valor`.
- RN2: Para números brasileiros, o link usa somente dígitos no número
  internacional, incluindo o código 55 uma única vez.
- RN3: O formato proposto da mensagem inclui o título do anúncio, conforme
  CA5, sujeito à confirmação do PO.
- RN4: Título e mensagem devem ser codificados de forma que seus caracteres
  não alterem a estrutura da URL.
- RN5: O utilitário não busca, fixa nem armazena números de contato; recebe os
  dados atuais que o chamador obtiver do perfil do anunciante.
- RN6: O utilitário não renderiza botões nem decide como apresentar a ausência
  de link; esses comportamentos pertencem a PROJ-51 e PROJ-52.

## Fora do escopo

- Botões, telas ou integração visual que consome o utilitário (PROJ-51).
- Fallback de exibição quando não houver link válido (PROJ-52).
- E-mail, chat interno ou intermediação financeira.
- Alterar o cadastro, armazenamento ou gerenciamento de contatos do anunciante.

## Dúvidas em aberto

- [NEEDS CLARIFICATION] A mensagem deve incluir o título ("Vi seu anúncio
  [Título]") ou usar a versão da Definition of Ready sem título?
- [NEEDS CLARIFICATION] O perfil permite números com outros códigos de país
  (D-013), enquanto esta feature descreve validação de números brasileiros.
  O utilitário deve rejeitar números internacionais ou gerar links para eles?
- [NEEDS CLARIFICATION] Qual deve ser o comportamento para título vazio ou só
  com espaços?
- [NEEDS CLARIFICATION] Há um limite de tamanho para o título/mensagem ou para
  a URL gerada? Como tratar títulos que excedam esse limite?
