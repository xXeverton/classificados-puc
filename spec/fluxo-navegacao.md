# Fluxo de navegação proposto

Proposta para alinhar telas, botões e links. Edite à vontade: renderiza no
GitHub, no VS Code (extensão Mermaid) e em https://mermaid.live.

## 1. Cabeçalho único (todas as telas autenticadas)

Mesmos itens, na mesma ordem, em todas as telas. A página atual recebe
`aria-current="page"`.

```mermaid
flowchart LR
  M["Logo PUC Classificados"] --> I["Início"]
  I --> MA["Meus anúncios"]
  MA --> P["Meu perfil"]
  P --> N["Botão: Novo anúncio"]
  N --> S["Botão: Sair"]
```

- Logo e "Início" levam a `/inicio/`.
- "Novo anúncio" é sempre botão primário (some o item de menu "Anunciar").
- Só `/inicio/` tem, além disso, busca e "Filtros".

## 2. Fluxo entre telas

```mermaid
flowchart TD
  RAIZ["/ (index)"] -->|sem sessão| ENTRAR
  RAIZ -->|com sessão| INICIO

  subgraph Publico["Sem login"]
    ENTRAR["/entrar/"]
    CADASTRO["/cadastro/"]
    CONFIRMAR["/confirmar-email/?token"]
    ENTRAR -->|Criar conta| CADASTRO
    CADASTRO -->|Já tenho conta| ENTRAR
    CADASTRO -->|e-mail enviado| EMAIL(["E-mail com link"])
    EMAIL --> CONFIRMAR
    CONFIRMAR -->|Ir para a entrada| ENTRAR
    CONFIRMAR -->|Cadastrar de novo| CADASTRO
  end

  ENTRAR -->|login ok| INICIO

  subgraph Logado["Com login (cabeçalho único)"]
    INICIO["/inicio/ (feed, busca, filtros)"]
    DETALHES["/anuncios/detalhes/?id"]
    MEUS["/meus-anuncios/"]
    PERFIL["/perfil/"]
    PERFILANUN["/perfil/anunciante/"]
    NOVO["/anuncios/novo/"]
    EDITAR["/anuncios/novo/?editar=id"]

    INICIO -->|clicar no card| DETALHES
    DETALHES -->|WhatsApp / E-mail| EXTERNO(["App externo"])
    DETALHES -->|"Editar anúncio (só o dono)"| EDITAR

    PERFIL -->|Editar / Completar perfil| PERFILANUN
    PERFILANUN -->|Salvar| PERFIL
    PERFILANUN -->|Cancelar| PERFIL
    PERFILANUN -->|"Salvar (depois=anunciar)"| NOVO
    PERFIL -->|Meus anúncios| MEUS

    NOVO -->|Publicar| INICIO
    NOVO -->|Cancelar| INICIO
    NOVO -->|perfil incompleto| PERFILANUN

    MEUS -->|Editar| EDITAR
    EDITAR -->|Salvar alterações| MEUS
    EDITAR -->|Cancelar| MEUS
    MEUS -->|"Excluir / Renovar / Vender / Reativar (na própria tela)"| MEUS
    MEUS -->|"Ver detalhes (só publicados)"| DETALHES
  end

  Logado -->|Sair| ENTRAR
  Logado -->|"401 / sessão expirada (?aviso=sessao_expirada)"| ENTRAR
```

Os caminhos "Ver detalhes" e "Editar anúncio" são novos (spec 013).

## 3. Decisões tomadas

Formalizadas na [spec 013](features/013-padronizar-navegacao-e-acoes/spec.md).

- [x] "Meus anúncios" no cabeçalho de todas as telas.
- [x] Sempre o botão azul "Novo anúncio"; sai o item "Anunciar".
- [x] "Cancelar" ao editar volta para Meus anúncios.
- [x] Dono do anúncio vê "Editar anúncio" nos detalhes (exige `is_owner` na API).
- [x] Cards de Meus anúncios ganham o botão "Ver detalhes" (não o título/imagem).
- [x] Padronizar rotas via `ROTAS` e imagens via `resolverUrlRecurso`.
