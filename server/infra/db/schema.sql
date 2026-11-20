-- Datas são gravadas em UTC, sem fuso, no formato padrão do SQLAlchemy.
-- Chaves estrangeiras exigem PRAGMA foreign_keys = ON em cada conexão.

CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL CHECK (length(trim(nome)) > 0),
    email TEXT NOT NULL UNIQUE CHECK (length(trim(email)) > 0),
    nome_usuario TEXT NOT NULL UNIQUE CHECK (
        length(trim(nome_usuario)) > 0 AND instr(nome_usuario, '@') = 0
    ),
    matricula TEXT UNIQUE CHECK (length(trim(matricula)) > 0),
    vinculo TEXT NOT NULL CHECK (vinculo IN ('aluno', 'funcionario')),
    senha_hash TEXT NOT NULL CHECK (length(trim(senha_hash)) > 0),
    confirmado_em DATETIME,
    tentativas_login_falhas INTEGER NOT NULL DEFAULT 0
        CHECK (tentativas_login_falhas >= 0),
    bloqueado_ate DATETIME
);

CREATE TABLE IF NOT EXISTS tokens_confirmacao (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER NOT NULL
        REFERENCES usuarios (id) ON DELETE CASCADE,
    token_hash TEXT NOT NULL UNIQUE,
    expira_em DATETIME NOT NULL,
    usado_em DATETIME
);

CREATE INDEX IF NOT EXISTS ix_tokens_confirmacao_usuario_id
    ON tokens_confirmacao (usuario_id);

CREATE TABLE IF NOT EXISTS sessoes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER NOT NULL
        REFERENCES usuarios (id) ON DELETE CASCADE,
    token_hash TEXT NOT NULL UNIQUE,
    criada_em DATETIME NOT NULL,
    expira_em DATETIME NOT NULL,
    revogada_em DATETIME
);

CREATE INDEX IF NOT EXISTS ix_sessoes_usuario_id ON sessoes (usuario_id);
