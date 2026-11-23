# Plano técnico: Aplicar o guia de estilo na tela de novo anúncio

Referência: `spec.md` desta pasta. Jira: PROJ-61.

Mudança só de front (HTML e CSS). Não há entidades, use cases, infra nem
rotas de API novas.

## Arquivos

| Arquivo | Mudança |
|---|---|
| `front/anuncios/novo/index.html` | Envolver o formulário em `.painel`; agrupar campos em `<section class="secao-anuncio">` com `h2` ("Sobre o anúncio", "Preço", "Foto"); preço com `fieldset.opcoes` + `label.opcoes__item`; rótulo da foto com `span.campo__opcional`; área "Sem foto" ao lado da prévia; contador e ajuda numa linha (`.campo__rodape`). IDs usados pelo JS ficam iguais (RN1). |
| `front/css/anuncios.css` | `.pagina` com a mesma largura do perfil (600px); `.secao-anuncio` igual a `.secao-perfil`; remover `.opcoes-preco*` (substituído por `.opcoes`); prévia com os tamanhos de `.perfil-foto`; `.campo__rodape` (ajuda à esquerda, contador à direita); só variáveis de `:root` (D-034). |
| `front/js/paginas/anuncios_novo.js` | Só se a área "Sem foto" precisar alternar com a prévia: esconder/mostrar `#foto-vazia` junto de `#foto-previa`. Nenhuma regra muda. |
| `front/guia-de-estilo/index.html` | Só se algum padrão novo passar a servir várias telas (ex.: seção de formulário). Nesse caso ele vai para `tema.css` **e** para o guia (D-034). |

## Decisões

- Reaproveitar os componentes do tema (`painel`, `formulario`, `campo`,
  `opcoes`, `botao`, `acoes`) antes de criar classes (D-034).
- A seção com título e linha divisória repete o padrão de `.secao-perfil`.
  Se for usada em mais telas no futuro, sobe para `tema.css` como componente
  genérico; por ora fica em `anuncios.css` para não mexer no perfil.
- A edição usa o mesmo HTML, então CA9 sai de graça.

## Estratégia de testes

- `front/tests/`: os testes de domínio atuais (`node --test`) precisam
  continuar passando; não há lógica nova para testar, salvo a alternância
  "Sem foto"/prévia se ela for para uma função de domínio.
- Roteiro manual no navegador (CA1 a CA12): criação e edição, com e sem foto,
  "Informar preço" e "A combinar", erros de validação, falha de conexão
  (API parada), desktop e celular (480 px), comparando com
  `/perfil/anunciante/` e `/guia-de-estilo/`.
