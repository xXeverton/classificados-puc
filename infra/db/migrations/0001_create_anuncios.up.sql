BEGIN IMMEDIATE;

CREATE TABLE anuncios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_anunciante INTEGER NOT NULL,
    titulo TEXT NOT NULL
        CHECK (
            length(titulo) BETWEEN 5 AND 80
            AND titulo = trim(titulo)
        ),
    descricao TEXT NOT NULL
        CHECK (
            length(trim(descricao)) > 0
            AND length(descricao) <= 500
        ),
    preco NUMERIC(12, 2)
        CHECK (
            preco IS NULL
            OR (
                typeof(preco) IN ('integer', 'real')
                AND preco >= 0
                AND preco <= 9999999999.99
                AND round(preco, 2) = preco
            )
        ),
    categoria TEXT NOT NULL
        CHECK (categoria IN ('produto', 'servico', 'evento')),
    estado_conservacao TEXT
        CHECK (
            estado_conservacao IS NULL
            OR estado_conservacao IN ('novo', 'usado_regular')
        ),
    created_at TEXT NOT NULL
        DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    FOREIGN KEY (id_anunciante)
        REFERENCES usuarios (id)
        ON DELETE CASCADE
);

CREATE INDEX idx_anuncios_id_anunciante
    ON anuncios (id_anunciante);
CREATE INDEX idx_anuncios_categoria
    ON anuncios (categoria);
CREATE INDEX idx_anuncios_created_at
    ON anuncios (created_at DESC);
CREATE INDEX idx_anuncios_categoria_created_at
    ON anuncios (categoria, created_at DESC);

PRAGMA user_version = 1;
COMMIT;
