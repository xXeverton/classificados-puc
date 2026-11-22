BEGIN IMMEDIATE;

CREATE TABLE ads_migracao (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL CHECK (length(trim(title)) > 0),
    description TEXT,
    type TEXT NOT NULL CHECK (type IN ('product', 'service', 'event')),
    category TEXT NOT NULL CHECK (length(trim(category)) > 0),
    price REAL NOT NULL,
    image_url TEXT,
    created_at DATETIME NOT NULL,
    status TEXT NOT NULL CHECK (
        status IN ('published', 'sold', 'expired')
    ),
    expires_at DATETIME,
    usuario_id INTEGER REFERENCES usuarios (id) ON DELETE CASCADE,
    estado_conservacao TEXT CHECK (
        estado_conservacao IS NULL OR
        estado_conservacao IN ('novo', 'usado_regular')
    ),
    preco_a_combinar INTEGER NOT NULL DEFAULT 0
        CHECK (preco_a_combinar IN (0, 1)),
    image_key TEXT
);

INSERT INTO ads_migracao (
    id, title, description, type, category, price, image_url,
    created_at, status, expires_at
)
SELECT
    id, title, description, type, category, price, image_url,
    created_at, status, expires_at
FROM ads;

DROP TABLE ads;
ALTER TABLE ads_migracao RENAME TO ads;
CREATE INDEX ix_ads_usuario_id ON ads (usuario_id);
PRAGMA user_version = 2;

COMMIT;
