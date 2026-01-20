-- =========================================================
-- TIPO_UTILIZADOR
-- =========================================================
CREATE OR REPLACE PROCEDURE sp_tipo_utilizador_create(
  p_designacao TEXT,
  OUT o_id INT
)
LANGUAGE plpgsql AS $$
BEGIN
  INSERT INTO public."Tipo_Utilizador"(designacao)
  VALUES (p_designacao)
  RETURNING id_tipo_utilizador INTO o_id;
END $$;

CREATE OR REPLACE PROCEDURE sp_tipo_utilizador_get(
  p_id int,
  INOUT cur refcursor
)
LANGUAGE plpgsql AS $$
BEGIN
  OPEN cur FOR
    SELECT * FROM Tipo_Utilizador WHERE id_tipo_utilizador = p_id;
END$$;

CREATE OR REPLACE PROCEDURE sp_tipo_utilizador_update(
  p_id int,
  p_designacao varchar DEFAULT NULL
)
LANGUAGE plpgsql AS $$
BEGIN
  UPDATE Tipo_Utilizador
     SET designacao = COALESCE(p_designacao, designacao)
   WHERE id_tipo_utilizador = p_id;
END$$;

CREATE OR REPLACE PROCEDURE sp_tipo_utilizador_delete(p_id int)
LANGUAGE plpgsql AS $$
BEGIN
  DELETE FROM Tipo_Utilizador WHERE id_tipo_utilizador = p_id;
END$$;

-- =========================================================
-- UTILIZADOR
-- =========================================================
CREATE OR REPLACE PROCEDURE sp_utilizador_create(
  p_nome varchar, p_email varchar, p_password varchar,
  p_morada text, p_nif char(9), p_imagem_perfil text, p_id_tipo_utilizador int,
  OUT o_id int
)
LANGUAGE plpgsql AS $$
BEGIN
  INSERT INTO Utilizador(nome, email, password, morada, nif, imagem_perfil, id_tipo_utilizador)
  VALUES (p_nome, p_email, p_password, p_morada, p_nif, p_imagem_perfil, p_id_tipo_utilizador)
  RETURNING id_utilizador INTO o_id;
END$$;

CREATE OR REPLACE PROCEDURE sp_utilizador_get(
  p_id int,
  INOUT cur refcursor
)
LANGUAGE plpgsql AS $$
BEGIN
  OPEN cur FOR SELECT * FROM Utilizador WHERE id_utilizador = p_id;
END$$;

CREATE OR REPLACE PROCEDURE sp_utilizador_update(
  p_id int,
  p_nome varchar DEFAULT NULL,
  p_email varchar DEFAULT NULL,
  p_password varchar DEFAULT NULL,
  p_morada text DEFAULT NULL,
  p_nif char(9) DEFAULT NULL,
  p_imagem_perfil text DEFAULT NULL,
  p_id_tipo_utilizador int DEFAULT NULL
)
LANGUAGE plpgsql AS $$
BEGIN
  UPDATE Utilizador SET
    nome = COALESCE(p_nome, nome),
    email = COALESCE(p_email, email),
    password = COALESCE(p_password, password),
    morada = COALESCE(p_morada, morada),
    nif = COALESCE(p_nif, nif),
    imagem_perfil = COALESCE(p_imagem_perfil, imagem_perfil),
    id_tipo_utilizador = COALESCE(p_id_tipo_utilizador, id_tipo_utilizador)
  WHERE id_utilizador = p_id;
END$$;

CREATE OR REPLACE PROCEDURE sp_utilizador_delete(p_id int)
LANGUAGE plpgsql AS $$
BEGIN
  DELETE FROM Utilizador WHERE id_utilizador = p_id;
END$$;

-- =========================================================
-- FORNECEDOR
-- =========================================================
CREATE OR REPLACE PROCEDURE sp_fornecedor_create(
  p_nome varchar, p_contacto varchar, p_email varchar,
  p_nif char(9), p_isSingular boolean, p_morada text, p_imagem text,
  OUT o_id int
)
LANGUAGE plpgsql AS $$
BEGIN
  INSERT INTO Fornecedor(nome, contacto, email, nif, isSingular, morada, imagem_fornecedor)
  VALUES (p_nome, p_contacto, p_email, p_nif, p_isSingular, p_morada, p_imagem)
  RETURNING id_fornecedor INTO o_id;
END$$;

CREATE OR REPLACE PROCEDURE sp_fornecedor_get(
  p_id int,
  INOUT cur refcursor
)
LANGUAGE plpgsql AS $$
BEGIN
  OPEN cur FOR SELECT * FROM Fornecedor WHERE id_fornecedor = p_id;
END$$;

CREATE OR REPLACE PROCEDURE sp_fornecedor_update(
  p_id int,
  p_nome varchar DEFAULT NULL,
  p_contacto varchar DEFAULT NULL,
  p_email varchar DEFAULT NULL,
  p_nif char(9) DEFAULT NULL,
  p_isSingular boolean DEFAULT NULL,
  p_morada text DEFAULT NULL,
  p_imagem text DEFAULT NULL
)
LANGUAGE plpgsql AS $$
BEGIN
  UPDATE Fornecedor SET
    nome = COALESCE(p_nome, nome),
    contacto = COALESCE(p_contacto, contacto),
    email = COALESCE(p_email, email),
    nif = COALESCE(p_nif, nif),
    isSingular = COALESCE(p_isSingular, isSingular),
    morada = COALESCE(p_morada, morada),
    imagem_fornecedor = COALESCE(p_imagem, imagem_fornecedor)
  WHERE id_fornecedor = p_id;
END$$;

CREATE OR REPLACE PROCEDURE sp_fornecedor_delete(p_id int)
LANGUAGE plpgsql AS $$
BEGIN
  DELETE FROM Fornecedor WHERE id_fornecedor = p_id;
END$$;

-- =========================================================
-- TIPO_PRODUTO
-- =========================================================
CREATE OR REPLACE PROCEDURE sp_tipo_produto_create(
  p_designacao varchar,
  OUT o_id int
)
LANGUAGE plpgsql AS $$
BEGIN
  INSERT INTO Tipo_Produto(designacao)
  VALUES (p_designacao)
  RETURNING id_tipo_produto INTO o_id;
END$$;

CREATE OR REPLACE PROCEDURE sp_tipo_produto_get(
  p_id int,
  INOUT cur refcursor
)
LANGUAGE plpgsql AS $$
BEGIN
  OPEN cur FOR SELECT * FROM Tipo_Produto WHERE id_tipo_produto = p_id;
END$$;

CREATE OR REPLACE PROCEDURE sp_tipo_produto_update(
  p_id int,
  p_designacao varchar DEFAULT NULL
)
LANGUAGE plpgsql AS $$
BEGIN
  UPDATE Tipo_Produto
     SET designacao = COALESCE(p_designacao, designacao)
   WHERE id_tipo_produto = p_id;
END$$;

CREATE OR REPLACE PROCEDURE sp_tipo_produto_delete(p_id int)
LANGUAGE plpgsql AS $$
BEGIN
  DELETE FROM Tipo_Produto WHERE id_tipo_produto = p_id;
END$$;

-- =========================================================
-- PRODUTO
-- =========================================================
CREATE OR REPLACE PROCEDURE sp_produto_create(
  p_nome varchar, p_descricao text, p_preco decimal, p_stock int,
  p_id_tipo_produto int, p_id_fornecedor int,
  OUT o_id int
)
LANGUAGE plpgsql AS $$
BEGIN
  INSERT INTO Produto(nome, descricao, preco, stock, id_tipo_produto, id_fornecedor)
  VALUES (p_nome, p_descricao, p_preco, p_stock, p_id_tipo_produto, p_id_fornecedor)
  RETURNING id_produto INTO o_id;
END$$;

CREATE OR REPLACE PROCEDURE sp_produto_get(
  p_id int,
  INOUT cur refcursor
)
LANGUAGE plpgsql AS $$
BEGIN
  OPEN cur FOR SELECT * FROM Produto WHERE id_produto = p_id;
END$$;

CREATE OR REPLACE PROCEDURE sp_produto_update(
  p_id int,
  p_nome varchar DEFAULT NULL,
  p_descricao text DEFAULT NULL,
  p_preco decimal DEFAULT NULL,
  p_stock int DEFAULT NULL,
  p_id_tipo_produto int DEFAULT NULL,
  p_id_fornecedor int DEFAULT NULL
)
LANGUAGE plpgsql AS $$
BEGIN
  UPDATE Produto SET
    nome = COALESCE(p_nome, nome),
    descricao = COALESCE(p_descricao, descricao),
    preco = COALESCE(p_preco, preco),
    stock = COALESCE(p_stock, stock),
    id_tipo_produto = COALESCE(p_id_tipo_produto, id_tipo_produto),
    id_fornecedor = COALESCE(p_id_fornecedor, id_fornecedor)
  WHERE id_produto = p_id;
END$$;

CREATE OR REPLACE PROCEDURE sp_produto_delete(p_id int)
LANGUAGE plpgsql AS $$
BEGIN
  DELETE FROM Produto WHERE id_produto = p_id;
END$$;

-- =========================================================
-- IMAGEM_PRODUTO
-- =========================================================
CREATE OR REPLACE PROCEDURE sp_imagem_produto_create(
  p_id_produto int, p_caminho text,
  OUT o_id int
)
LANGUAGE plpgsql AS $$
BEGIN
  INSERT INTO Imagem_Produto(id_produto, caminho)
  VALUES (p_id_produto, p_caminho)
  RETURNING id_imagem INTO o_id;
END$$;

CREATE OR REPLACE PROCEDURE sp_imagem_produto_get(
  p_id int,
  INOUT cur refcursor
)
LANGUAGE plpgsql AS $$
BEGIN
  OPEN cur FOR SELECT * FROM Imagem_Produto WHERE id_imagem = p_id;
END$$;

CREATE OR REPLACE PROCEDURE sp_imagem_produto_update(
  p_id int,
  p_id_produto int DEFAULT NULL,
  p_caminho text DEFAULT NULL
)
LANGUAGE plpgsql AS $$
BEGIN
  UPDATE Imagem_Produto SET
    id_produto = COALESCE(p_id_produto, id_produto),
    caminho = COALESCE(p_caminho, caminho)
  WHERE id_imagem = p_id;
END$$;

CREATE OR REPLACE PROCEDURE sp_imagem_produto_delete(p_id int)
LANGUAGE plpgsql AS $$
BEGIN
  DELETE FROM Imagem_Produto WHERE id_imagem = p_id;
END$$;

-- =========================================================
-- ESTADO_CARRINHO
-- =========================================================
CREATE OR REPLACE PROCEDURE sp_estado_carrinho_create(
  p_descricao varchar,
  OUT o_id int
)
LANGUAGE plpgsql AS $$
BEGIN
  INSERT INTO Estado_Carrinho(descricao)
  VALUES (p_descricao)
  RETURNING id_estado INTO o_id;
END$$;

CREATE OR REPLACE PROCEDURE sp_estado_carrinho_get(
  p_id int,
  INOUT cur refcursor
)
LANGUAGE plpgsql AS $$
BEGIN
  OPEN cur FOR SELECT * FROM Estado_Carrinho WHERE id_estado = p_id;
END$$;

CREATE OR REPLACE PROCEDURE sp_estado_carrinho_update(
  p_id int,
  p_descricao varchar DEFAULT NULL
)
LANGUAGE plpgsql AS $$
BEGIN
  UPDATE Estado_Carrinho SET
    descricao = COALESCE(p_descricao, descricao)
  WHERE id_estado = p_id;
END$$;

CREATE OR REPLACE PROCEDURE sp_estado_carrinho_delete(p_id int)
LANGUAGE plpgsql AS $$
BEGIN
  DELETE FROM Estado_Carrinho WHERE id_estado = p_id;
END$$;

-- =========================================================
-- CARRINHO  (CORRIGIDA ORDEM DO OUT vs DEFAULT)
-- =========================================================
CREATE OR REPLACE PROCEDURE sp_carrinho_create(
  p_id_utilizador int,
  OUT o_id int,
  p_estado int DEFAULT NULL
)
LANGUAGE plpgsql AS $$
BEGIN
  INSERT INTO Carrinho(id_utilizador, estado)
  VALUES (p_id_utilizador, p_estado)
  RETURNING id_carrinho INTO o_id;
END$$;

CREATE OR REPLACE PROCEDURE sp_carrinho_get(
  p_id int,
  INOUT cur refcursor
)
LANGUAGE plpgsql AS $$
BEGIN
  OPEN cur FOR SELECT * FROM Carrinho WHERE id_carrinho = p_id;
END$$;

CREATE OR REPLACE PROCEDURE sp_carrinho_update(
  p_id int,
  p_id_utilizador int DEFAULT NULL,
  p_estado int DEFAULT NULL
)
LANGUAGE plpgsql AS $$
BEGIN
  UPDATE Carrinho SET
    id_utilizador = COALESCE(p_id_utilizador, id_utilizador),
    estado = COALESCE(p_estado, estado)
  WHERE id_carrinho = p_id;
END$$;

CREATE OR REPLACE PROCEDURE sp_carrinho_delete(p_id int)
LANGUAGE plpgsql AS $$
BEGIN
  DELETE FROM Carrinho WHERE id_carrinho = p_id;
END$$;

-- =========================================================
-- PRODUTO_CARRINHO (ponte)
-- =========================================================
CREATE OR REPLACE PROCEDURE sp_produto_carrinho_create(
  p_id_carrinho int, p_id_produto int, p_quantidade int DEFAULT 1
)
LANGUAGE plpgsql AS $$
BEGIN
  INSERT INTO Produto_Carrinho(id_carrinho, id_produto, quantidade)
  VALUES (p_id_carrinho, p_id_produto, p_quantidade)
  ON CONFLICT (id_carrinho, id_produto)
  DO UPDATE SET quantidade = EXCLUDED.quantidade;
END$$;

CREATE OR REPLACE PROCEDURE sp_produto_carrinho_get(
  p_id_carrinho int, p_id_produto int,
  INOUT cur refcursor
)
LANGUAGE plpgsql AS $$
BEGIN
  OPEN cur FOR
    SELECT * FROM Produto_Carrinho
     WHERE id_carrinho = p_id_carrinho AND id_produto = p_id_produto;
END$$;

CREATE OR REPLACE PROCEDURE sp_produto_carrinho_update(
  p_id_carrinho int, p_id_produto int, p_quantidade int
)
LANGUAGE plpgsql AS $$
BEGIN
  UPDATE Produto_Carrinho
     SET quantidade = p_quantidade
   WHERE id_carrinho = p_id_carrinho AND id_produto = p_id_produto;
END$$;

CREATE OR REPLACE PROCEDURE sp_produto_carrinho_delete(
  p_id_carrinho int, p_id_produto int
)
LANGUAGE plpgsql AS $$
BEGIN
  DELETE FROM Produto_Carrinho
  WHERE id_carrinho = p_id_carrinho AND id_produto = p_id_produto;
END$$;

-- =========================================================
-- TIPO_NOTICIA
-- =========================================================
CREATE OR REPLACE PROCEDURE sp_tipo_noticia_create(
  p_nome varchar,
  OUT o_id int
)
LANGUAGE plpgsql AS $$
BEGIN
  INSERT INTO Tipo_Noticia(nome)
  VALUES (p_nome)
  RETURNING id_tipo_noticia INTO o_id;
END$$;

CREATE OR REPLACE PROCEDURE sp_tipo_noticia_get(
  p_id int,
  INOUT cur refcursor
)
LANGUAGE plpgsql AS $$
BEGIN
  OPEN cur FOR SELECT * FROM Tipo_Noticia WHERE id_tipo_noticia = p_id;
END$$;

CREATE OR REPLACE PROCEDURE sp_tipo_noticia_update(
  p_id int,
  p_nome varchar DEFAULT NULL
)
LANGUAGE plpgsql AS $$
BEGIN
  UPDATE Tipo_Noticia
     SET nome = COALESCE(p_nome, nome)
   WHERE id_tipo_noticia = p_id;
END$$;

CREATE OR REPLACE PROCEDURE sp_tipo_noticia_delete(p_id int)
LANGUAGE plpgsql AS $$
BEGIN
  DELETE FROM Tipo_Noticia WHERE id_tipo_noticia = p_id;
END$$;

-- =========================================================
-- NOTICIA
-- =========================================================
CREATE OR REPLACE PROCEDURE sp_noticia_create(
  p_titulo varchar, p_conteudo varchar,
  p_id_tipo_noticia int, p_autor int, p_data_publicacao date,
  OUT o_id int
)
LANGUAGE plpgsql AS $$
BEGIN
  INSERT INTO Noticia(titulo, conteudo, id_tipo_noticia, autor, data_publicacao)
  VALUES (p_titulo, p_conteudo, p_id_tipo_noticia, p_autor, p_data_publicacao)
  RETURNING id_noticia INTO o_id;
END$$;

CREATE OR REPLACE PROCEDURE sp_noticia_get(
  p_id int,
  INOUT cur refcursor
)
LANGUAGE plpgsql AS $$
BEGIN
  OPEN cur FOR SELECT * FROM Noticia WHERE id_noticia = p_id;
END$$;

CREATE OR REPLACE PROCEDURE sp_noticia_update(
  p_id int,
  p_titulo varchar DEFAULT NULL,
  p_conteudo varchar DEFAULT NULL,
  p_id_tipo_noticia int DEFAULT NULL,
  p_autor int DEFAULT NULL,
  p_data_publicacao date DEFAULT NULL
)
LANGUAGE plpgsql AS $$
BEGIN
  UPDATE Noticia SET
    titulo = COALESCE(p_titulo, titulo),
    conteudo = COALESCE(p_conteudo, conteudo),
    id_tipo_noticia = COALESCE(p_id_tipo_noticia, id_tipo_noticia),
    autor = COALESCE(p_autor, autor),
    data_publicacao = COALESCE(p_data_publicacao, data_publicacao)
  WHERE id_noticia = p_id;
END$$;

CREATE OR REPLACE PROCEDURE sp_noticia_delete(p_id int)
LANGUAGE plpgsql AS $$
BEGIN
  DELETE FROM Noticia WHERE id_noticia = p_id;
END$$;

-- =========================================================
-- IMAGEM_NOTICIA
-- =========================================================
CREATE OR REPLACE PROCEDURE sp_imagem_noticia_create(
  p_id_noticia int, p_uri text,
  OUT o_id int
)
LANGUAGE plpgsql AS $$
BEGIN
  INSERT INTO Imagem_Noticia(id_noticia, uri)
  VALUES (p_id_noticia, p_uri)
  RETURNING id_imagem INTO o_id;
END$$;

CREATE OR REPLACE PROCEDURE sp_imagem_noticia_get(
  p_id int,
  INOUT cur refcursor
)
LANGUAGE plpgsql AS $$
BEGIN
  OPEN cur FOR SELECT * FROM Imagem_Noticia WHERE id_imagem = p_id;
END$$;

CREATE OR REPLACE PROCEDURE sp_imagem_noticia_update(
  p_id int,
  p_id_noticia int DEFAULT NULL,
  p_uri text DEFAULT NULL
)
LANGUAGE plpgsql AS $$
BEGIN
  UPDATE Imagem_Noticia SET
    id_noticia = COALESCE(p_id_noticia, id_noticia),
    uri = COALESCE(p_uri, uri)
  WHERE id_imagem = p_id;
END$$;

CREATE OR REPLACE PROCEDURE sp_imagem_noticia_delete(p_id int)
LANGUAGE plpgsql AS $$
BEGIN
  DELETE FROM Imagem_Noticia WHERE id_imagem = p_id;
END$$;

-- =========================================================
-- PRODUTO_NOTICIA (ponte)
-- =========================================================
CREATE OR REPLACE PROCEDURE sp_produto_noticia_create(
  p_id_noticia int, p_id_produto int
)
LANGUAGE plpgsql AS $$
BEGIN
  INSERT INTO Produto_Noticia(id_noticia, id_produto)
  VALUES (p_id_noticia, p_id_produto)
  ON CONFLICT DO NOTHING;
END$$;

CREATE OR REPLACE PROCEDURE sp_produto_noticia_get(
  p_id_noticia int, p_id_produto int,
  INOUT cur refcursor
)
LANGUAGE plpgsql AS $$
BEGIN
  OPEN cur FOR
    SELECT * FROM Produto_Noticia
     WHERE id_noticia = p_id_noticia AND id_produto = p_id_produto;
END$$;

CREATE OR REPLACE PROCEDURE sp_produto_noticia_delete(
  p_id_noticia int, p_id_produto int
)
LANGUAGE plpgsql AS $$
BEGIN
  DELETE FROM Produto_Noticia
  WHERE id_noticia = p_id_noticia AND id_produto = p_id_produto;
END$$;
