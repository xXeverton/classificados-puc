# Plano tecnico: Utilitario para gerar link de contato do WhatsApp

Referencia: `spec.md` desta pasta.

Dependencias:

- Contatos do anunciante seguem D-013. Nesta feature, o numero fornecido pode
  chegar com mascara, com DDI separado ou incorporado ao texto informado pelo
  chamador.
- A interface consumidora e o fallback visual ficam fora desta feature
  (PROJ-51 e PROJ-52).
- D-030 exige front-end em JavaScript puro sem framework ou dependencias.

## Dominio (`front/js/dominio/`)

- Criar uma funcao pura que receba o numero fornecido pelo chamador e o titulo
  do anuncio.
- Normalizar o numero removendo caracteres nao numericos.
- Preservar um DDI internacional explicito indicado por "+" ou "00".
- Acrescentar o codigo internacional brasileiro 55 quando o numero nao tiver
  DDI explicito.
- Aceitar numeros normalizados com 8 a 15 digitos.
- Montar a mensagem fixa aprovada pela especificacao e codificar o texto para
  uso seguro em URL.
- Usar a mensagem generica sem titulo quando o titulo estiver vazio ou tiver
  apenas espacos.
- Preservar titulos longos integralmente, sem truncamento.
- Retornar o link completo quando os dados forem validos e uma resposta clara
  de indisponibilidade quando o numero nao permitir geracao.
- Nao acessar DOM, rede, armazenamento, estado global ou perfil diretamente.
- Usar o numero recebido em cada chamada, sem cache ou valor fixo.

## Contratos

O modulo de dominio devera expor uma funcao de geracao de link com parametros
independentes:

- `numero`: texto recebido do contato atual do perfil.
- `titulo`: titulo do anuncio.

A resposta sera:

- uma string `https://wa.me/{numero}?text={mensagem}` quando valida; ou
- `null` quando o numero estiver ausente ou invalido.

As decisoes sobre mostrar ou ocultar elementos permanecem na interface
consumidora.

## Interface web (`front/`)

- Nenhuma tela sera criada ou alterada nesta subtarefa.
- Um chamador futuro em PROJ-51 fornecera o numero atual do perfil e o titulo.
- Nenhum contato sera buscado ou armazenado pelo modulo.

## Estrutura e principios SOLID aplicados

- O modulo no dominio tera uma unica responsabilidade: validar entradas,
  normalizar o numero e montar o link.
- A funcao sera pura e recebera todos os dados necessarios como parametros,
  permitindo testes isolados e reutilizacao.
- Variaveis e regras de formato serao centralizadas no modulo, evitando
  numeros, textos ou formatos magicos espalhados.

## Estrategia de testes

- Escrever os testes em `front/tests/` antes da implementacao.
- Cobrir numero com mascara, com e sem codigo 55, numero ausente ou nao
  numerico, titulo com acentos, emojis e caracteres reservados da URL.
- Cobrir chamadas consecutivas com numeros diferentes para garantir ausencia de
  cache ou numero fixo.
- Validar numeros normalizados com 8 a 15 digitos.
- Executar `make front-test`.
- As regras aqui descritas nao exigem banco de dados, API, entidades de servidor,
  use cases ou alteracao de schema.
