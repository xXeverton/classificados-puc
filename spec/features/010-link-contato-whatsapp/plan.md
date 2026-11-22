# Plano técnico: Utilitário para gerar link de contato do WhatsApp

Referência: `spec.md` desta pasta.

Dependências:

- Contatos de WhatsApp do perfil de anunciante seguem D-013 e fornecem
  `codigo_pais` e `valor`.
- A interface consumidora e o fallback visual ficam fora desta feature
  (PROJ-51 e PROJ-52).
- As decisões em aberto da spec precisam ser resolvidas antes da aprovação.

## Domínio (`front/js/dominio/`)

- Criar uma função pura para normalizar e validar o número e montar o link e a
  mensagem codificada.
- Não acessar rede, DOM, armazenamento ou estado global.
- Receber explicitamente o número atual como string e o título do anúncio; o
  chamador combina `codigo_pais` e `valor` conforme RN1.
- Não manter uma cópia do contato do vendedor.
- Retornar a URL quando os dados permitirem a geração e `null` quando o número
  não for válido.
- Validar somente as regras de país e tamanho que forem confirmadas na spec.

## Casos de uso

Nenhum caso de uso de backend é necessário. A geração é uma transformação
local e reutilizável do front-end; a interface que a consome está em PROJ-51.

## Infraestrutura

Nenhuma mudança em banco de dados, API ou dependências externas é necessária.

## Interface web (`front/`)

- Módulo sugerido: `front/js/dominio/link_whatsapp.js`.
- O chamador fornecerá os dados atuais do contato do perfil e o título do
  anúncio.
- Esta feature não cria ou altera telas, botões ou o tratamento visual de
  retorno `null`.

## Princípios SOLID aplicados

- A função mantém uma única responsabilidade: validar/normalizar a entrada e
  construir o link.
- A transformação recebe dados como parâmetros e não depende de estado
  externo, o que permite reutilização e testes isolados.

## Estratégia de testes

- `front/tests/`: testar número brasileiro com máscara, com e sem código 55,
  número ausente/inválido e títulos com acentos, emojis e caracteres que
  poderiam alterar a URL.
- Cobrir entradas distintas para confirmar que o link usa o número passado
  naquela chamada, sem valor fixo ou estado residual.
- Usar `node --test` / `make front-test`.
- `pytest` e `flake8` não se aplicam a esta mudança restrita ao JavaScript do
  front-end.
