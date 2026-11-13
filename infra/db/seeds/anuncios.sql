INSERT INTO usuarios (nome, email, matricula, vinculo) VALUES
    ('Ana Silva', 'ana.seed@example.com', 'seed-ana', 'aluno'),
    ('Bruno Costa', 'bruno.seed@example.com', 'seed-bruno', 'aluno');

INSERT INTO anuncios (
    id_anunciante, titulo, descricao, preco, categoria, estado_conservacao
) VALUES
    (
        (SELECT id FROM usuarios WHERE matricula = 'seed-ana'),
        'Bicicleta urbana aro 29',
        'Bicicleta revisada, pronta para uso.',
        850.00,
        'produto',
        'usado_regular'
    ),
    (
        (SELECT id FROM usuarios WHERE matricula = 'seed-ana'),
        'Aulas de matematica',
        'Aulas particulares para ensino medio.',
        NULL,
        'servico',
        NULL
    ),
    (
        (SELECT id FROM usuarios WHERE matricula = 'seed-bruno'),
        'Feira comunitaria',
        'Evento aberto para a comunidade.',
        0.00,
        'evento',
        NULL
    );
