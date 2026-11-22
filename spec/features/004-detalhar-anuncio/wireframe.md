# Wireframe textual: Detalhar anúncio

Fonte: descrição da história Jira [PROJ-17](https://matheuscomputacaopuc.atlassian.net/browse/PROJ-17).

## Estrutura desktop

- Cabeçalho comum da plataforma.
- Conteúdo principal dividido em duas áreas:
  - esquerda: foto ou galeria do anúncio;
  - direita: bloco com título, categoria, estado de conservação, preço,
    descrição completa e informações do item.
- Abaixo ou no bloco direito: painel do anunciante com nome de exibição,
  vínculo e foto, quando houver.
- No painel do anunciante: botões ou links dos contatos cadastrados.

## Estrutura móvel

- Cabeçalho comum.
- Foto ou estado sem foto acima das informações.
- Informações do item em sequência vertical.
- Bloco do anunciante abaixo das informações.
- Contatos em botões ou links que cabem na largura da tela.
- Não deve haver rolagem horizontal.

## Estados

- Carregamento: indicar que os dados estão sendo buscados.
- Sem foto: manter o bloco visual do lado esquerdo ou acima, sem quebrar o
  layout, sem apresentar galeria vazia. Texto: "Este anúncio não possui foto."
- Sem sessão: "Faça login para ver os detalhes do anúncio."
- Anúncio inexistente: "Anúncio não encontrado."
- Anúncio vendido: "Este anúncio já foi vendido e não está mais disponível para contato."
- Anúncio expirado: "Este anúncio expirou e não está mais disponível para contato."
- Anúncio excluído: "Este anúncio foi excluído ou não está mais disponível."
- Anúncio não publicado: "Este anúncio não está publicado."
- Anúncio vendido, expirado, excluído ou não publicado: mensagem
  específica do estado e sem contato disponível.
- Falha de API ou conexão: "Não foi possível carregar o anúncio. Tente novamente."
