# Spec: Comportamento dos botões de contato quando falta uma forma

- **ID**: 012
- **Status**: Implementada
- **Data**: 2026-11-22
- **Jira**: PROJ-52
- **Decisões gerais aplicadas**: D-013, D-030, D-032, D-034, D-051
- **Depende de**: PROJ-50 e PROJ-51

## História de usuário

**Como** comprador,
**quero** ver apenas os botões de contato que realmente podem ser utilizados,
**para que** eu não clique em uma opção quebrada.

**Como** comprador,
**quero** continuar tendo um caminho claro de contato quando o vendedor não
informou WhatsApp ou e-mail,
**para que** eu saiba quais opções estão disponíveis.

## Critérios de aceitação

- [x] CA1: Dado um vendedor com WhatsApp e e-mail válidos, quando a página do
  anúncio abre, então os dois botões são exibidos e ativados.
- [x] CA2: Dado um vendedor com apenas e-mail válido e sem WhatsApp válido,
  quando a página abre, então apenas “Enviar E-mail” é exibido.
- [x] CA3: Dado um vendedor com apenas WhatsApp válido e sem e-mail válido,
  quando a página abre, então apenas “Chamar no WhatsApp” é exibido.
- [x] CA4: Dado um número de WhatsApp inválido segundo a regra da PROJ-50 e um
  e-mail válido, quando a página abre, então o WhatsApp fica ausente e o e-mail
  continua disponível.
- [x] CA5: Dado que um dos dois contatos ficou ausente, quando a página abre,
  então o botão disponível ocupa o destaque visual definido pela página sem
  deixar espaço vazio ou quebrar o layout.
- [x] CA6: Dado que o vendedor não informou nenhum WhatsApp nem e-mail válido,
  quando a página abre, então os dois botões são exibidos desabilitados.
- [x] CA7: Dado que o vendedor atualizou seus contatos no perfil, quando o
  anúncio é recarregado, então os botões refletem o perfil atual.

## Regras de negócio

- RN1: O WhatsApp é considerado disponível somente quando existe um contato do
  tipo `whatsapp` cujo valor produz um link válido pela regra da PROJ-50.
- RN2: O e-mail é considerado disponível somente quando existe um contato do
  tipo `email` válido.
- RN3: Para a combinação WhatsApp + e-mail, os dois botões são exibidos e
  ativos.
- RN4: Para apenas um dos dois contatos, somente o botão correspondente é
  exibido.
- RN5: Para nenhum dos dois contatos válidos, os dois botões são exibidos
  desabilitados, sem link, função de clique ou navegação externa.
- RN6: O resultado é calculado a partir da lista atual fornecida pela página;
  não há cache nem cópia local dos contatos do vendedor.
- RN7: Contatos não relacionados a WhatsApp ou e-mail não devem ser removidos
  pela regra desta feature.

## Mensagens e rótulos

- WhatsApp ativo: `Chamar no WhatsApp`.
- E-mail ativo: `Enviar E-mail`.
- Nenhum dos dois disponível: ambos os rótulos permanecem visíveis e os botões
  permanecem desabilitados.

## Fora de escopo

- Normalização ou validação definitiva do número no cadastro, definida pela
  PROJ-50.
- Criação dos links em si, definida pela PROJ-51.
- Editar contatos do perfil.
- Outros tipos de contato, como telefone, site e link.
- Alterar a obrigatoriedade de ao menos um contato no perfil (D-010/D-013).

## Dúvidas em aberto

Nenhuma dúvida pendente.
