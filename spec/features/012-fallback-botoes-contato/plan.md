# Plano técnico: Comportamento dos botões de contato

Referência: `spec.md` desta pasta.

Dependências:

- D-013 define a lista atual de contatos do anunciante.
- D-030 exige HTML, CSS e JavaScript puros.
- D-032 e D-034 exigem componentes do tema e do guia de estilo.
- PROJ-50 fornece a validação e o link do WhatsApp.
- PROJ-51 fornece os rótulos e os links ativos.

## Domínio (`front/js/dominio/`)

- Criar uma função para classificar os contatos disponíveis em:
  - WhatsApp ativo;
  - e-mail ativo;
  - ambos ausentes.
- Reutilizar o utilitário da PROJ-50 para confirmar se o WhatsApp é válido.
- Reutilizar a construção de `mailto:` da PROJ-51.
- Não armazenar estado ou cache de disponibilidade.
- Retornar dados simples suficientes para a página decidir quais elementos
  renderizar.

## Página existente (`front/anuncios/detalhes/`)

- Renderizar somente o botão WhatsApp quando ele estiver disponível e o e-mail
  estiver ausente.
- Renderizar somente o botão e-mail no caso inverso.
- Renderizar os dois ativos quando ambos estiverem disponíveis.
- Quando ambos estiverem ausentes, renderizar os dois rótulos em botões
  desabilitados.
- Remover `href`, `target` e `rel` dos elementos desabilitados.
- Usar o componente `botao` já existente e o CSS próprio da página para
  estado visual desabilitado.
- Não criar espaço reservado vazio nem alterar os demais contatos.

## Contratos

A entrada continua sendo a lista atual de contatos e o título do anúncio:

- WhatsApp válido: gera link ativo pela PROJ-50/51.
- E-mail válido: gera `mailto:` ativo pela PROJ-51.
- Ambos inválidos ou ausentes: cria botões desabilitados.

Não há alteração em endpoint, banco de dados ou modelo persistido.

## Princípios SOLID aplicados

- A classificação de disponibilidade fica separada da renderização visual.
- A página usa a classificação para decidir o conteúdo sem conter validação
  duplicada.
- As regras dependem de funções puras e entradas explícitas.

## Estratégia de testes

- Testes unitários em `front/tests/detalhes.test.js` para:
  - ambos disponíveis;
  - somente e-mail;
  - somente WhatsApp;
  - WhatsApp inválido;
  - ambos ausentes;
  - perfil atualizado em chamadas sucessivas.
- Testes da renderização para verificar remoção de links e estado desabilitado.
- `make front-test` passa.
