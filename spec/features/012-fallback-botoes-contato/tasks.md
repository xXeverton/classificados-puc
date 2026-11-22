# Tarefas: Fallback dos botões de contato

Referências: `spec.md` e `plan.md` desta pasta.
Marque `[x]` ao concluir. Escreva os testes antes da implementação.

Status atual: **Implementada**. Os testes e a implementação foram concluídos
conforme D-051.

## Contrato e testes

- [x] T1: Escrever testes para ambos os contatos disponíveis.
- [x] T2: Escrever testes para somente e-mail e somente WhatsApp.
- [x] T3: Escrever testes para WhatsApp inválido.
- [x] T4: Escrever testes para ambos ausentes e botões desabilitados.
- [x] T5: Escrever testes que confirmem uso dos contatos atuais em cada
  renderização.

## Implementação

- [x] T6: Criar classificação pura dos contatos disponíveis.
- [x] T7: Atualizar a página detalhada para esconder o botão indisponível.
- [x] T8: Renderizar os dois botões desabilitados quando ambos estiverem
  ausentes.
- [x] T9: Manter outros tipos de contato e o layout sem espaço quebrado.
- [x] T10: Confirmar que elementos desabilitados não possuem link nem ação.

## Validação

- [x] T11: `make front-test` passa.
- [x] T12: Critérios de aceitação aprovados cobertos por testes.
