BEGIN;

-- =========================
-- TIPO_UTILIZADOR
-- =========================
INSERT INTO Tipo_Utilizador (id_tipo_utilizador, designacao) VALUES
  (1, 'Administrador'),
  (2, 'Funcionário');
  (3, 'Cliente');

-- =========================
-- UTILIZADOR
-- =========================
INSERT INTO Utilizador (id_utilizador, nome, email, password, morada, nif, imagem_perfil, id_tipo_utilizador) VALUES
  (1, 'Ana Silva',   'ana.silva@example.com',   'hash_password_ana',   'Rua das Flores 10, Lisboa', '123456789', '/imgs/utilizadores/1.png', 1),
  (2, 'Bruno Costa', 'bruno.costa@example.com', 'hash_password_bruno', 'Av. do Mar 200, Porto',     '987654321', '/imgs/utilizadores/2.png', 2);

-- =========================
-- FORNECEDOR
-- Nota: isSingular = true permite morada NULL; se false, morada é obrigatória
-- =========================
INSERT INTO Fornecedor (id_fornecedor, nome, contacto, email, nif, isSingular, morada, imagem_fornecedor) VALUES
  (1, 'Quinta do Vale', '+351912345678', 'contacto@qvale.pt', '111222333', true,  NULL,                              '/imgs/fornecedores/1.png'),
  (2, 'Alimentos SA',   '+351210000000', 'geral@alimentos.sa', '222333444', false, 'Parque Industrial, Lote 5, Braga','/imgs/fornecedores/2.png');

-- =========================
-- TIPO_PRODUTO
-- =========================
INSERT INTO Tipo_Produto (id_tipo_produto, designacao) VALUES
  (1, 'Bebidas'),
  (2, 'Mercearia');

SELECT setval('tipo_produto_id_tipo_produto_seq', 2, true);

-- =========================
-- PRODUTO
-- =========================
INSERT INTO Produto (id_produto, nome, descricao, preco, stock, id_tipo_produto, id_fornecedor) VALUES
  (1, 'Sumo de Laranja 1L', 'Sumo 100% laranja, sem adição de açúcar.', 1.99, 100, 1, 1),
  (2, 'Bolachas de Aveia',  'Bolachas crocantes de aveia integral.',     2.49,  50, 2, 2);

SELECT setval('produto_id_produto_seq', 2, true);

-- =========================
-- IMAGEM_PRODUTO
-- =========================
INSERT INTO Imagem_Produto (id_imagem, id_produto, caminho) VALUES
  (1, 1, '/imgs/produtos/1.png'),
  (2, 2, '/imgs/produtos/2.png');

SELECT setval('imagem_produto_id_imagem_seq', 2, true);

-- =========================
-- ESTADO_CARRINHO
-- =========================
INSERT INTO Estado_Carrinho (id_estado, descricao) VALUES
  (1, 'Aberto'),
  (2, 'Pago'),
  (3, 'Cancelado');

SELECT setval('estado_carrinho_id_estado_seq', 3, true);

-- =========================
-- CARRINHO
-- =========================
INSERT INTO Carrinho (id_carrinho, id_utilizador, estado) VALUES
  (1, 1, 1),  -- Ana, Aberto
  (2, 2, 2);  -- Bruno, Pago

SELECT setval('carrinho_id_carrinho_seq', 2, true);

-- =========================
-- PRODUTO_CARRINHO
-- =========================
INSERT INTO Produto_Carrinho (id_carrinho, id_produto, quantidade) VALUES
  (1, 1, 2),  -- Carrinho 1 tem 2x Sumo
  (1, 2, 1),  -- Carrinho 1 tem 1x Bolachas
  (2, 2, 3);  -- Carrinho 2 tem 3x Bolachas

-- =========================
-- TIPO_NOTICIA
-- =========================
INSERT INTO Tipo_Noticia (id_tipo_noticia, nome) VALUES
  (1, 'Promoção'),
  (2, 'Lançamento');

SELECT setval('tipo_noticia_id_tipo_noticia_seq', 2, true);

-- =========================
-- NOTICIA
-- =========================
INSERT INTO Noticia (id_noticia, titulo, conteudo, id_tipo_noticia, autor, data_publicacao) VALUES
  (1, 'Campanha de Verão', 'Descontos até 30% em bebidas selecionadas durante o mês.', 1, 1, DATE '2025-06-01'),
  (2, 'Novo Produto: Bolachas de Aveia', 'Chegaram as novas bolachas de aveia integral!', 2, 2, DATE '2025-06-15');

SELECT setval('noticia_id_noticia_seq', 2, true);

-- =========================
-- IMAGEM_NOTICIA
-- =========================
INSERT INTO Imagem_Noticia (id_imagem, id_noticia, uri) VALUES
  (1, 1, '/imgs/noticias/1a.jpg'),
  (2, 1, '/imgs/noticias/1b.jpg'),
  (3, 2, '/imgs/noticias/2a.jpg');

SELECT setval('imagem_noticia_id_imagem_seq', 3, true);

-- =========================
-- PRODUTO_NOTICIA
-- =========================
INSERT INTO Produto_Noticia (id_noticia, id_produto) VALUES
  (1, 1),  -- Campanha de Verão destaca Sumo
  (2, 2);  -- Lançamento destaca Bolachas

COMMIT;
