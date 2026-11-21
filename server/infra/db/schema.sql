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

-- Perfil de anunciante: extensão opcional de usuarios (no máximo um por
-- usuário). Ter linha aqui é ser anunciante. O mínimo de 1 e o máximo de 10
-- contatos e a ausência de contatos repetidos são garantidos pela entidade
-- Anunciante, não pelo banco.
CREATE TABLE IF NOT EXISTS anunciantes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER NOT NULL UNIQUE
        REFERENCES usuarios (id) ON DELETE CASCADE,
    nome_exibicao TEXT NOT NULL CHECK (length(trim(nome_exibicao)) > 0),
    foto_url TEXT CHECK (foto_url IS NULL OR length(trim(foto_url)) > 0)
);

-- Contatos do anunciante, na ordem escolhida pela pessoa (posicao).
-- tipo: whatsapp, telefone, email, site ou link.
-- codigo_pais: obrigatório em telefone, opcional em whatsapp (vazio = por
-- link) e proibido nos demais. valor: número só com dígitos (quando há
-- codigo_pais), e-mail ou endereço https.
CREATE TABLE IF NOT EXISTS contatos_anunciante (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    anunciante_id INTEGER NOT NULL
        REFERENCES anunciantes (id) ON DELETE CASCADE,
    posicao INTEGER NOT NULL CHECK (posicao >= 0),
    tipo TEXT NOT NULL
        CHECK (tipo IN ('whatsapp', 'telefone', 'email', 'site', 'link')),
    codigo_pais TEXT,
    valor TEXT NOT NULL CHECK (length(trim(valor)) > 0),
    rotulo TEXT,
    UNIQUE (anunciante_id, posicao),
    CHECK (
        CASE tipo
            WHEN 'telefone' THEN codigo_pais IS NOT NULL
            WHEN 'whatsapp' THEN 1
            ELSE codigo_pais IS NULL
        END
    ),
    -- Número: código com 1 a 3 dígitos e, junto com o número, 8 a 15 dígitos.
    CHECK (
        codigo_pais IS NULL OR (
            length(codigo_pais) BETWEEN 1 AND 3
            AND codigo_pais NOT GLOB '*[^0-9]*'
            AND valor NOT GLOB '*[^0-9]*'
            AND length(codigo_pais) + length(valor) BETWEEN 8 AND 15
        )
    ),
    -- WhatsApp por link: só wa.me ou api.whatsapp.com, com algo no caminho.
    CHECK (
        tipo <> 'whatsapp' OR codigo_pais IS NOT NULL OR (
            valor NOT GLOB '*[ ]*' AND (
                valor LIKE 'https://wa.me/_%'
                OR valor LIKE 'https://api.whatsapp.com/_%'
            )
        )
    ),
    CHECK (tipo <> 'email' OR instr(valor, '@') > 1),
    CHECK (
        tipo NOT IN ('site', 'link') OR (
            valor LIKE 'https://_%' AND valor NOT GLOB '*[ ]*'
        )
    ),
    CHECK (rotulo IS NULL OR (tipo = 'link' AND length(trim(rotulo)) > 0))
);
