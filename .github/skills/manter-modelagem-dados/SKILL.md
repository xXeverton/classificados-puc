---
name: manter-modelagem-dados
description: "Use whenever persistent data, database entities, tables, columns, fields, constraints, or relationships are added, changed, renamed, or removed. Keep the SQLite schema, database model README, migrations, and tests synchronized."
---

# Manter a modelagem de dados

Use esta skill sempre que uma implementação adicionar, alterar ou remover
qualquer dado persistido, incluindo entidades, tabelas, colunas, restrições,
relacionamentos, índices ou formatos armazenados.

## Procedimento

1. Leia `infra/db/README.md`, `infra/db/schema.sql`, o inicializador do banco e
   os testes existentes antes de propor alterações.
2. Determine se a mudança afeta bancos novos, bancos já existentes, ou ambos.
   O schema com `CREATE TABLE IF NOT EXISTS` não atualiza tabelas existentes.
3. Preserve dados existentes. Se a alteração exigir migração, implemente uma
   migração explícita e testável; se a regra de transformação ou remoção não
   estiver definida, pergunte antes de descartar ou modificar dados.
4. Atualize o schema e o código de inicialização/migração para refletir o
   modelo desejado.
5. Atualize `infra/db/README.md`, sua tabela de campos, restrições e diagrama.
   Atualize também o `README.md` raiz se os procedimentos ou localização
   documentados mudarem.
6. Adicione ou ajuste testes para constraints, migração e comportamento de
   persistência afetado.
7. Execute os testes relacionados e `flake8`; relate qualquer validação que
   não pôde ser executada.

## Regras

- Mantenha nomes, tipos, obrigatoriedade, unicidade e demais constraints
  consistentes entre código, schema, documentação e testes.
- Não assuma valores padrão nem regras de negócio que não estejam especificadas.
- Mudanças destrutivas ou perda de dados exigem confirmação explícita do usuário.
- Não marque a mudança como concluída enquanto a documentação e os testes do
  modelo não estiverem sincronizados.
