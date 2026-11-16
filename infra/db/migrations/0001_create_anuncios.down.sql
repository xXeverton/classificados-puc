BEGIN IMMEDIATE;

DROP INDEX IF EXISTS idx_anuncios_categoria_created_at;
DROP INDEX IF EXISTS idx_anuncios_created_at;
DROP INDEX IF EXISTS idx_anuncios_categoria;
DROP INDEX IF EXISTS idx_anuncios_id_anunciante;
DROP TABLE IF EXISTS anuncios;

PRAGMA user_version = 0;
COMMIT;
