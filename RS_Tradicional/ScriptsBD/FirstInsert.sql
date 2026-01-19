-- ==========================
-- DADOS INICIAIS
-- ==========================

-- TIPOS DE UTILIZADOR
INSERT INTO Tipo_Utilizador (designacao) VALUES
    ('Admin'),
    ('Gestor'),
    ('Cliente');

-- UTILIZADORES (ADMIN / GESTOR / CLIENTE)
-- Substituir <HASH_...> pelas hashes reais geradas com make_password
INSERT INTO Utilizador (nome, email, password, morada, nif, id_tipo_utilizador) VALUES
    ('Administrador RS', 'admin@rstradicional.pt',  '<HASH_ADMIN>',  'Rua Principal 1, Viseu', '111111111', 1),
    ('Gestor RS',        'gestor@rstradicional.pt', '<HASH_GESTOR>', 'Av. Central 25, Viseu',  '222222222', 2),
    ('Cliente Teste',    'cliente@rstradicional.pt','<HASH_CLIENTE>','Rua do Cliente 3, Viseu','333333333', 3);

-- FORNECEDOR EXEMPLO
INSERT INTO Fornecedor (nome, contacto, email, nif, isSingular, morada, imagem_fornecedor) VALUES
    ('Queijaria da Serra', '+351912345678', 'contato@queijariadaserra.pt', '444444444',
     FALSE, 'Parque Industrial, Armazém 4, Gouveia', '/imagens/fornecedores/queijaria_serra.png');

-- TIPOS DE PRODUTO
INSERT INTO Tipo_Produto (designacao) VALUES
    ('Queijos Tradicionais'),
    ('Enchidos Regionais');

-- PRODUTOS
-- 1: produto já aprovado e ativo (criado pela própria loja / gestor)
INSERT INTO Produto (nome, descricao, preco, stock, is_approved, estado_produto, id_tipo_produto, id_fornecedor) VALUES
    ('Queijo da Serra DOP',
     'Queijo curado de ovelha, cura mínima de 60 dias.',
     14.50,
     20,
     TRUE,
     'Ativo',
     1,   -- Queijos Tradicionais
     1);  -- Queijaria da Serra

-- 2: produto ainda PENDENTE (imagina que foi sugerido por fornecedor/gestor)
INSERT INTO Produto (nome, descricao, preco, stock, is_approved, estado_produto, id_tipo_produto, id_fornecedor) VALUES
    ('Queijo de Cabra Curado',
     'Queijo curado de cabra, sabor intenso.',
     9.90,
     15,
     FALSE,
     'Pendente',
     1,
     1);

-- IMAGENS DOS PRODUTOS (OPCIONAL)
INSERT INTO Imagem_Produto (id_produto, caminho) VALUES
    (1, '/imagens/produtos/queijo_serra_dop.jpg'),
    (2, '/imagens/produtos/queijo_cabra_curado.jpg');

-- TIPOS DE NOTÍCIA
INSERT INTO Tipo_Noticia (nome) VALUES
    ('Promoções'),
    ('Novidades');

-- NOTÍCIA EXEMPLO
INSERT INTO Noticia (titulo, conteudo, id_tipo_noticia, autor, data_publicacao) VALUES
    ('Bem-vindo à RS Tradicional',
     'A nossa loja online já está em funcionamento com os melhores produtos regionais.',
     2,   -- Novidades
     1,   -- Autor: Admin
     CURRENT_DATE);

-- IMAGEM DA NOTÍCIA (OPCIONAL)
INSERT INTO Imagem_Noticia (id_noticia, uri) VALUES
    (1, '/imagens/noticias/boas_vindas.jpg');

-- PRODUTO EM DESTAQUE NA NOTÍCIA
INSERT INTO Produto_Noticia (id_noticia, id_produto) VALUES
    (1, 1);

-- ENCOMENDA EXEMPLO (CLIENTE TESTE)
INSERT INTO Encomenda (data_encomenda, id_utilizador, estado_encomenda) VALUES
    (CURRENT_DATE, 3, 'Pendente');

-- LINHAS DA ENCOMENDA (cliente comprou 2 unidades do Queijo da Serra)
INSERT INTO Encomendas_Produtos (id_encomenda, id_produto, quantidade) VALUES
    (1, 1, 2);


-- Tipo de Utilizador Fornecedor (se ainda não existir)
INSERT INTO Tipo_Utilizador (designacao)
VALUES ('Fornecedor');

-- Utilizador que representa um fornecedor
-- Substitui <HASH_FORNECEDOR> por uma hash gerada com make_password("fornecedor123"), por ex.
INSERT INTO Utilizador (nome, email, password, morada, nif, id_tipo_utilizador)
VALUES (
    'Fornecedor Queijaria',
    'fornecedor@queijariadaserra.pt',
    '<HASH_FORNECEDOR>',
    'Parque Industrial, Armazém 4, Gouveia',
    '555555555',
    (SELECT id_tipo_utilizador FROM Tipo_Utilizador WHERE designacao = 'Fornecedor')
);

-- Fornecedor com o MESMO email (para conseguirmos associar)
INSERT INTO Fornecedor (nome, contacto, email, nif, isSingular, morada, imagem_fornecedor)
VALUES (
    'Queijaria da Serra',
    '+351912345678',
    'fornecedor@queijariadaserra.pt',
    '444444444',
    FALSE,
    'Parque Industrial, Armazém 4, Gouveia',
    '/imagens/fornecedores/queijaria_serra.png'
);
