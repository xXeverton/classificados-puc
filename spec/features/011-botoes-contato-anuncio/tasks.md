# Tarefas: Botões de contato na página do anúncio

Referências: `spec.md` e `plan.md` desta pasta.
Marque `[x]` ao concluir. Escreva os testes antes da implementação.

Status atual: **Implementada**. Os testes e a implementação foram concluídos
conforme D-051.

## Contrato e testes

- [x] T1: Escrever testes para os rótulos “Chamar no WhatsApp” e
  “Enviar E-mail”.
- [x] T2: Escrever testes que confirmem o link do WhatsApp com mensagem
  pré-preenchida e título atual.
- [x] T3: Escrever testes que confirmem o `mailto:` com destinatário, assunto,
  corpo e caracteres especiais codificados.
- [x] T4: A implementação usa `target="_blank"` e relação segura; validada por
  revisão do código da página.
- [x] T5: Escrever testes que usem contatos atualizados em chamadas sucessivas,
  sem cache ou valor fixo.

## Implementação

- [x] T6: Criar ou ampliar o módulo de domínio da página para montar os links
  de WhatsApp e e-mail.
- [x] T7: Atualizar a renderização da página detalhada para mostrar os rótulos
  aprovados e abrir os links externos em nova aba.
- [x] T8: Preservar o comportamento dos demais tipos de contato já exibidos.
- [x] T9: Confirmar que a implementação não usa `innerHTML` e segue D-034.

## Validação

- [x] T10: `make front-test` passa.
- [x] T11: Cada critério de aceitação aprovado está coberto por teste ou
  validação manual registrada.
