# Spec: Aplicar o guia de estilo na tela de novo anúncio

- **ID**: 014
- **Status**: Aprovada
- **Data**: 2026-11-23
- **Jira**: subtarefa [PROJ-61](https://matheuscomputacaopuc.atlassian.net/browse/PROJ-61)
  da task PROJ-54 (épico PROJ-10)
- **Decisões gerais aplicadas**: D-032, D-034, D-035
- **Relacionadas**: [007-editar-excluir-anuncio](../007-editar-excluir-anuncio/spec.md),
  [013-padronizar-navegacao-e-acoes](../013-padronizar-navegacao-e-acoes/spec.md)

## Contexto

A tela de novo anúncio (`/anuncios/novo/`, também usada para editar) destoa
das outras telas com formulário, como o perfil de anunciante:

- o formulário fica solto sobre o fundo cinza, sem o cartão branco (`painel`)
  que as outras telas usam;
- a largura da página é diferente da do perfil;
- as opções de preço usam um componente próprio em vez de `opcoes` do guia;
- "Foto (opcional)" escreve "(opcional)" no rótulo em vez de usar o estilo de
  campo opcional do guia;
- a foto não tem a área de prévia/"Sem foto" que o perfil usa;
- não há separação visual entre os grupos de informação.

Esta feature só muda a aparência. Regras, validações, mensagens e o envio
continuam como estão (specs de anúncio e 007).

## História de usuário

**Como** membro que vai anunciar,
**quero** que a tela de novo anúncio tenha a mesma aparência das outras telas
da plataforma,
**para que** ela pareça parte do mesmo produto e seja fácil de preencher.

## Critérios de aceitação

- [ ] CA1: Dado a tela de novo anúncio, quando ela abre, então o formulário
  aparece dentro de um cartão branco com borda e cantos arredondados, como no
  perfil de anunciante.
- [ ] CA2: Dado a tela de novo anúncio, então a largura do conteúdo, o
  espaçamento do topo e o título seguem os mesmos valores do perfil de
  anunciante.
- [ ] CA3: Dado o formulário, então os campos ficam agrupados em seções com
  título: "Sobre o anúncio" (título, categoria, estado de conservação e
  descrição), "Preço" e "Foto", separadas por uma linha suave, como as seções
  do perfil.
- [ ] CA4: Dado as opções "Informar preço" e "A combinar", então elas têm a
  mesma aparência das opções em rádio do guia de estilo.
- [ ] CA5: Dado o campo de valor, então o "R$" aparece junto do campo, alinhado
  a ele, sem quebrar o tamanho da entrada.
- [ ] CA6: Dado o campo da foto, então o rótulo mostra "(opcional)" no estilo
  de campo opcional do guia, e sem foto escolhida aparece a área "Sem foto"
  no lugar da prévia, como no perfil; ao escolher uma foto, a prévia ocupa
  esse lugar e o botão "Remover foto" aparece ao lado.
- [ ] CA7: Dado os contadores de caracteres (título e descrição), então eles
  ficam alinhados à direita, na mesma linha da ajuda do campo.
- [ ] CA8: Dado os botões "Publicar" e "Cancelar", então eles ficam no fim do
  cartão, no mesmo padrão das ações do perfil.
- [ ] CA9: Dado a tela aberta para **editar** um anúncio, então ela tem a
  mesma aparência da criação (só o título e o texto do botão mudam, como hoje).
- [ ] CA10: Dado um celular (até 480 px), então não há rolagem horizontal, os
  botões ocupam a largura toda e a prévia da foto cabe na tela (D-032).
- [ ] CA11: Dado erros de validação, a falha de conexão e o envio em
  andamento, então eles aparecem como hoje (mensagens junto dos campos, alerta
  no topo, botão indisponível), agora com o visual do guia.
- [ ] CA12: Dado a página `/guia-de-estilo/`, então todo componente usado na
  tela existe nela; nenhum valor de cor ou medida fica solto no CSS da tela
  (D-034).

## Regras de negócio

- RN1: Nenhuma regra, validação, mensagem ou chamada à API muda. Os
  identificadores usados pelo script da tela continuam os mesmos.

## Fora do escopo

- Mais de uma foto por anúncio.
- Mudanças em outras telas (detalhes, painel, início).
- Mudar textos de ajuda ou mensagens.

## Dúvidas em aberto

- Nenhuma. A divisão em seções (CA3) e os títulos delas foram propostos com
  base no perfil de anunciante e devem ser confirmados na aprovação.
