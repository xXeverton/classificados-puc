# Tarefas: Utilitario para gerar link de contato do WhatsApp

Referencias: `spec.md` e `plan.md` desta pasta.
Marque `[x]` ao concluir. Escreva os testes antes da implementacao.

Status atual: **Aprovada**. Implemente conforme D-051, com testes antes do
codigo de producao.

## Contrato e testes

- [x] T1: Registrar na implementacao os formatos confirmados: mascara no numero,
  DDI explicito preservado, codigo 55 para numero sem DDI, titulo generico
  vazio e preservacao integral de titulo longo.
- [x] T2: Escrever testes em `front/tests/` para numero mundial e brasileiro
  com mascara, codigo 55 com e sem duplicacao, numero ausente ou fora de
  8 a 15 digitos e codificacao da mensagem.
- [x] T3: Escrever testes que enviem numeros diferentes em chamadas distintas
  para verificar que o utilitario nunca fixa ou reutiliza o numero do
  anunciante.
- [x] T4: Escrever testes para titulo vazio, apenas espacos, acentos, emojis,
  caracteres reservados da URL e titulo longo sem truncamento.

## Implementacao

- [x] T5: Implementar o modulo puro em `front/js/dominio/` que normaliza o
  numero e monta o link.
- [x] T6: Confirmar que o modulo nao acessa DOM, rede, armazenamento ou estado
  global e nao depende de dados persistidos.

## Validacao

- [x] T7: `make front-test` passa.
- [x] T8: Cada criterio de aceitacao aprovado esta coberto por ao menos um
  teste.
