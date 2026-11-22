# Spec: Utilitario para gerar link de contato do WhatsApp

- **ID**: 010
- **Status**: Implementada
- **Data**: 2026-11-22
- **Jira**: PROJ-50
- **Decisoes gerais aplicadas**: D-013, D-030, D-051
- **Relacionadas**: PROJ-51 (interface consumidora) e PROJ-52 (fallback de
  exibicao)

## Historia de usuario

**Como** desenvolvedor da interface,
**quero** gerar um link do WhatsApp a partir do numero atual do anunciante e do
titulo do anuncio,
**para que** todos os pontos de contato usem uma mesma regra e o comprador possa
iniciar uma conversa com uma mensagem preenchida.

**Como** comprador,
**quero** abrir o WhatsApp com uma mensagem sobre o anuncio,
**para que** eu nao precise digita-la manualmente.

## Criterios de aceitacao

- [x] CA1: Dado o numero "(21) 98765-4321" e o titulo "Bicicleta Caloi",
  quando o link e solicitado, entao o numero normalizado usa somente digitos,
  recebe o codigo 55 e o resultado inicia com
  `https://wa.me/5521987654321?text=`.
- [x] CA2: Dado um numero sem codigo do pais, mas com DDD e numero brasileiro,
  quando o link e solicitado, entao o numero recebe o codigo 55 uma unica vez.
- [x] CA3: Dado um numero ja internacionalizado como "+55 21 98765-4321",
  quando o link e solicitado, entao o codigo 55 nao aparece duplicado.
- [x] CA4: Dado o numero valido "(21) 98765-4321" e o titulo "Bicicleta Caloi",
  quando o link e gerado, entao a mensagem pre-formatada e
  "Olá! Vi seu anúncio Bicicleta Caloi no PUC pra Rolo e tenho interesse.".
- [x] CA5: Dado um titulo com acentos, emojis ou caracteres especiais,
  quando o link e gerado, entao a mensagem e codificada para URL e chega
  intacta ao WhatsApp sem quebrar ou truncar a URL.
- [x] CA5.1: Dado um titulo vazio ou composto apenas por espacos, quando o
  link e gerado, entao a mensagem usa
  "Olá! Vi seu anúncio no PUC pra Rolo e tenho interesse.".
- [x] CA5.2: Dado um titulo muito longo, quando o link e gerado, entao o titulo
  completo e utilizado sem qualquer limite ou truncamento.
- [x] CA6: Dado um numero vazio, formado apenas por caracteres nao numericos
  ou com tamanho fora do intervalo valido de 8 a 15 digitos, quando o link e
  solicitado, entao o utilitario informa que nao ha link valido sem lancar
  excecao.
- [x] CA6.1: Dado um numero mundial com mascara e DDI explicito, quando o link
  e solicitado, entao o numero e normalizado com o DDI recebido, sem adicionar
  o codigo brasileiro 55.
- [x] CA6.2: Dado um numero com mascara sem DDI explicito, quando o link e
  solicitado, entao o codigo 55 e acrescido automaticamente.
- [x] CA7: Dado que o perfil atual fornece o numero do anunciante, quando o
  link e solicitado em chamadas distintas, entao o numero usado em cada chamada
  corresponde ao numero recebido e nao a um numero fixo ou armazenado
  anteriormente pelo utilitario.

## Regras de negocio

- RN1: O numero vem dos contatos atuais do perfil do anunciante (D-013), sem
  busca, copia ou armazenamento pelo utilitario.
- RN2: O numero pode representar telefone fixo ou celular, brasileiro ou
  mundial. Entradas com mascara sao aceitas e caracteres nao numericos sao
  removidos. Um numero valido pode conter de 8 a 15 digitos apos a normalizacao.
- RN3: Numeros brasileiros sem DDI explicito usam somente digitos e incluem o
  codigo 55 uma
  unica vez.
- RN3.1: Quando o numero recebido tiver DDI explicito em formato internacional,
  como "+" ou "00", esse DDI sera preservado. Quando nao houver DDI explicito,
  sera considerado brasileiro e recebera o codigo 55.
- RN4: A mensagem inclui o titulo do anuncio conforme o criterio adotado nesta
  especificacao. Quando o titulo estiver vazio ou tiver apenas espacos, a
  mensagem usa o texto generico sem titulo.
- RN5: Espacos, acentos, emojis e caracteres especiais do titulo nao podem
  alterar a estrutura da URL.
- RN5.1: Titulos muito longos nao sao truncados nem impedem a geracao do link.
- RN6: A ausencia ou invalidade do numero deve produzir uma resposta de falha
  controlada. O utilitario nao decide ocultar botao nem renderizar fallback;
  esses comportamentos pertencem a PROJ-51 e PROJ-52.

## Fora do escopo

- Interface, botoes e tela de detalhes do anuncio (PROJ-51).
- Ocultar ou substituir o botao quando nao houver link valido (PROJ-52).
- Cadastro ou alteracao dos contatos do anunciante.
- Chat interno, e-mail, telefone convencional e intermediacao financeira.
- Alteracao das mensagens ou textos em outras telas.

## Duvidas em aberto

Nenhuma duvida pendente.
