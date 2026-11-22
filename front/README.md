# Interface web (`front/`)

HTML, CSS e JavaScript puros, sem build nem dependências de npm. Rode a API e
o servidor de desenvolvimento do front:

```bash
make front        # frontend + proxy da API em http://localhost:5173
make front-test   # testes do front (Node 18 ou mais novo)
```

O servidor do front encaminha as rotas da API para `127.0.0.1:5000`, usando a
mesma origem do navegador. Assim, login e demais chamadas funcionam também
quando o Codespaces encaminha apenas a porta 5173 para o navegador.

## Telas

`/entrar/`, `/cadastro/`, `/confirmar-email/`, `/inicio/`, `/perfil/`,
`/perfil/anunciante/` e `/anuncios/novo/` (provisória).

## Organização

`paginas/` → `fluxos/` → `dominio/`; `adaptadores/` fala HTTP com a API (veja
[ARQUITETURA.md](../ARQUITETURA.md)). O endereço da API fica em
`js/config.js`.

## Estilo

O visual comum está em `css/tema.css`, com demonstração em `/guia-de-estilo/`.
Use as variáveis e classes do tema antes de criar estilos novos.

Quando o backend for usado por outras pessoas, `CONFIRMACAO_URL_BASE` (veja
[server/README.md](../server/README.md)) precisa apontar para o front
publicado.
