# Interface web (`front/`)

HTML, CSS e JavaScript puros, sem build nem dependências de npm. Com a API
rodando e `CORS_ORIGINS=http://localhost:5173`:

```bash
make front        # servidor em http://localhost:5173
make front-test   # testes do front (Node 18 ou mais novo)
```

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
