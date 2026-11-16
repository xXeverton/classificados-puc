CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL CHECK (length(trim(nome)) > 0),
    email TEXT NOT NULL UNIQUE CHECK (length(trim(email)) > 0),
    matricula TEXT NOT NULL UNIQUE CHECK (length(trim(matricula)) > 0),
    vinculo TEXT NOT NULL CHECK (length(trim(vinculo)) > 0)
);

CREATE TABLE IF NOT EXISTS ads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL CHECK (length(trim(title)) > 0),
    description TEXT,
    type TEXT NOT NULL CHECK (type IN ('product', 'service')),
    category TEXT NOT NULL CHECK (length(trim(category)) > 0),
    price REAL NOT NULL,
    image_url TEXT,
    created_at DATETIME NOT NULL,
    status TEXT NOT NULL CHECK (
        status IN ('published', 'sold', 'expired')
    ),
    expires_at DATETIME
);
