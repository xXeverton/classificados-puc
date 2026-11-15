CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL CHECK (length(trim(nome)) > 0),
    email TEXT NOT NULL UNIQUE CHECK (length(trim(email)) > 0),
    matricula TEXT NOT NULL UNIQUE CHECK (length(trim(matricula)) > 0),
    vinculo TEXT NOT NULL CHECK (length(trim(vinculo)) > 0)
);
