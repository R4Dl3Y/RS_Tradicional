-- 02_functions_views.sql
-- Funções de apoio e Views de listagem

-- =========================
-- DROPS
-- =========================

DROP FUNCTION IF EXISTS fn_get_tipo_utilizador(INT);
DROP FUNCTION IF EXISTS fn_get_utilizador_por_email(TEXT);
DROP FUNCTION IF EXISTS fn_encomenda_total(INT);

DROP VIEW IF EXISTS vw_admin_utilizadores CASCADE;
DROP VIEW IF EXISTS vw_tipos_utilizador CASCADE;
DROP VIEW IF EXISTS vw_tipos_produto CASCADE;
DROP VIEW IF EXISTS vw_fornecedores CASCADE;
DROP VIEW IF EXISTS vw_admin_produtos CASCADE;
DROP VIEW IF EXISTS vw_loja_produtos CASCADE;
DROP VIEW IF EXISTS vw_admin_encomendas CASCADE;
DROP VIEW IF EXISTS vw_encomendas_produtos CASCADE;
DROP VIEW IF EXISTS vw_noticias CASCADE;
DROP VIEW IF EXISTS vw_admin_noticias CASCADE;
DROP VIEW IF EXISTS vw_tipos_noticia CASCADE;
DROP VIEW IF EXISTS vw_admin_encomenda_linhas CASCADE;
DROP VIEW IF EXISTS vw_cliente_encomendas CASCADE;
DROP VIEW IF EXISTS vw_cliente_encomenda_detalhe CASCADE;
DROP VIEW IF EXISTS vw_loja_carrinho CASCADE;
DROP VIEW IF EXISTS vw_loja_carrinho_linhas CASCADE;
DROP VIEW IF EXISTS vw_fornecedor_produtos CASCADE;
DROP VIEW IF EXISTS vw_conta_fornecedor_perfil CASCADE;
DROP VIEW IF EXISTS vw_conta_perfil CASCADE;
DROP VIEW IF EXISTS vw_fornecedor_encomendas CASCADE;
DROP VIEW IF EXISTS vw_fornecedor_encomenda_linhas CASCADE;



-- =========================
-- FUNÇÃO: tipo de utilizador
-- =========================

CREATE OR REPLACE FUNCTION fn_get_tipo_utilizador(p_id_utilizador INT)
RETURNS TEXT
LANGUAGE plpgsql
AS $$
DECLARE
    v_tipo TEXT;
BEGIN
    SELECT tu.designacao
    INTO v_tipo
    FROM Utilizador u
    LEFT JOIN Tipo_Utilizador tu
           ON tu.id_tipo_utilizador = u.id_tipo_utilizador
    WHERE u.id_utilizador = p_id_utilizador;

    RETURN v_tipo;
END;
$$;


-- =========================
-- FUNÇÃO: utilizador por email (para login)
-- =========================


CREATE OR REPLACE FUNCTION fn_get_utilizador_por_email(p_email text)
RETURNS TABLE (
    id_utilizador      INTEGER,
    nome               VARCHAR(100),
    email              VARCHAR(255),
    password           VARCHAR(255),
    morada             TEXT,
    nif                CHAR(9),
    id_tipo_utilizador INTEGER,
    tipo_designacao    VARCHAR(50)
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        u.id_utilizador,
        u.nome,
        u.email,
        u.password,
        u.morada,
        u.nif,
        u.id_tipo_utilizador,
        tu.designacao
    FROM Utilizador u
    LEFT JOIN Tipo_Utilizador tu
           ON tu.id_tipo_utilizador = u.id_tipo_utilizador
    WHERE LOWER(u.email) = LOWER(p_email);
END;
$$;


-- =========================
-- FUNÇÃO: total da encomenda
-- =========================

CREATE OR REPLACE FUNCTION fn_encomenda_total(p_id_encomenda INT)
RETURNS NUMERIC
LANGUAGE plpgsql
AS $$
DECLARE
    v_total NUMERIC := 0;
BEGIN
    SELECT
        COALESCE(SUM(ep.quantidade * p.preco), 0)
    INTO v_total
    FROM Encomendas_Produtos ep
    JOIN Produto p ON p.id_produto = ep.id_produto
    WHERE ep.id_encomenda = p_id_encomenda;

    RETURN v_total;
END;
$$;


-- =========================
-- VIEW: Utilizadores + Tipo
-- =========================

CREATE OR REPLACE VIEW vw_admin_utilizadores AS
SELECT
    u.id_utilizador,
    u.nome,
    u.email,
    u.password,
    u.morada,
    u.nif,
    u.id_tipo_utilizador,
    tu.designacao AS tipo_designacao
FROM Utilizador u
LEFT JOIN Tipo_Utilizador tu
       ON tu.id_tipo_utilizador = u.id_tipo_utilizador;


-- =========================
-- VIEW: Tipos de Utilizador
-- =========================

CREATE OR REPLACE VIEW vw_tipos_utilizador AS
SELECT
    id_tipo_utilizador,
    designacao
FROM Tipo_Utilizador;


-- =========================
-- VIEW: Tipos de Produto
-- =========================

CREATE OR REPLACE VIEW vw_tipos_produto AS
SELECT
    id_tipo_produto,
    designacao
FROM Tipo_Produto;


-- =========================
-- VIEW: Fornecedores
-- =========================

CREATE OR REPLACE VIEW vw_fornecedores AS
SELECT
    f.id_fornecedor,
    f.nome,
    f.contacto,
    f.email,
    f.nif,
    f.isSingular,
    f.morada,
    f.imagem_fornecedor
FROM Fornecedor f;


-- =========================
-- VIEW: Produtos (admin)
-- =========================

CREATE OR REPLACE VIEW vw_admin_produtos AS
SELECT
    p.id_produto,
    p.nome,
    p.descricao,
    p.preco,
    p.stock,
    p.is_approved,
    p.estado_produto,
    p.id_tipo_produto,
    tp.designacao AS tipo_designacao,
    p.id_fornecedor,
    f.nome AS fornecedor_nome
FROM Produto p
LEFT JOIN Tipo_Produto tp
       ON tp.id_tipo_produto = p.id_tipo_produto
LEFT JOIN Fornecedor f
       ON f.id_fornecedor = p.id_fornecedor;


-- =========================
-- VIEW: Produtos loja (apenas ativos + aprovados)
-- =========================

CREATE OR REPLACE VIEW vw_loja_produtos AS
SELECT
    p.id_produto,
    p.nome,
    p.descricao,
    p.preco,
    p.stock,
    p.id_tipo_produto,
    tp.designacao AS tipo_designacao,
    p.id_fornecedor,
    f.nome AS fornecedor_nome
FROM Produto p
LEFT JOIN Tipo_Produto tp ON tp.id_tipo_produto = p.id_tipo_produto
LEFT JOIN Fornecedor f ON f.id_fornecedor = p.id_fornecedor
WHERE p.is_approved = TRUE
  AND p.estado_produto = 'Ativo'
  AND p.stock > 0;



-- =========================
-- VIEW: Encomendas (admin)
-- =========================

CREATE OR REPLACE VIEW vw_admin_encomendas AS
SELECT
    e.id_encomenda,
    e.data_encomenda,
    e.id_utilizador,
    u.nome AS utilizador_nome,
    u.email AS utilizador_email,
    e.estado_encomenda,
    fn_encomenda_total(e.id_encomenda) AS total_encomenda
FROM Encomenda e
JOIN Utilizador u ON u.id_utilizador = e.id_utilizador;


-- =========================
-- VIEW: Linhas de Encomenda
-- =========================

CREATE OR REPLACE VIEW vw_encomendas_produtos AS
SELECT
    ep.id_encomenda,
    ep.id_produto,
    ep.quantidade,
    p.nome  AS produto_nome,
    p.preco AS produto_preco
FROM Encomendas_Produtos ep
JOIN Produto p ON p.id_produto = ep.id_produto;



CREATE OR REPLACE VIEW vw_admin_encomenda_linhas AS
SELECT
    id_encomenda,
    id_produto,
    quantidade,
    produto_nome  AS nome_produto,
    produto_preco AS preco_produto
FROM vw_encomendas_produtos;


CREATE OR REPLACE VIEW vw_cliente_encomendas AS
SELECT
    e.id_encomenda,
    e.data_encomenda,
    e.estado_encomenda,
    e.id_utilizador
FROM Encomenda e
WHERE e.estado_encomenda <> 'Carrinho';


CREATE OR REPLACE VIEW vw_cliente_encomenda_detalhe AS
SELECT
    ep.id_encomenda,
    ep.id_produto,
    p.nome  AS nome_produto,
    p.preco AS preco_produto,
    ep.quantidade
FROM Encomendas_Produtos ep
JOIN Produto p ON p.id_produto = ep.id_produto;



-- =========================
-- VIEW: Notícias
-- =========================

CREATE OR REPLACE VIEW vw_noticias AS
SELECT
    n.id_noticia,
    n.titulo,
    n.conteudo,
    n.data_publicacao,
    n.id_tipo_noticia,
    tn.nome AS tipo_noticia_nome,
    n.autor      AS id_autor,
    u.nome       AS autor_nome,
    u.email      AS autor_email
FROM Noticia n
LEFT JOIN Tipo_Noticia tn ON tn.id_tipo_noticia = n.id_tipo_noticia
LEFT JOIN Utilizador  u  ON u.id_utilizador = n.autor;


CREATE OR REPLACE VIEW vw_admin_noticias AS
SELECT
    n.id_noticia,
    n.titulo,
    n.conteudo,
    n.data_publicacao,
    n.id_tipo_noticia,
    tn.nome AS tipo_noticia,
    n.autor AS autor_id,
    u.nome  AS autor_nome
FROM Noticia n
LEFT JOIN Tipo_Noticia tn ON tn.id_tipo_noticia = n.id_tipo_noticia
LEFT JOIN Utilizador u    ON u.id_utilizador = n.autor;



CREATE OR REPLACE VIEW vw_tipos_noticia AS
SELECT
    id_tipo_noticia,
    nome
FROM Tipo_Noticia;


CREATE OR REPLACE VIEW vw_loja_carrinho AS
SELECT
    e.id_encomenda,
    e.data_encomenda,
    e.estado_encomenda,
    e.id_utilizador
FROM Encomenda e
WHERE e.estado_encomenda = 'Carrinho';


CREATE OR REPLACE VIEW vw_loja_carrinho_linhas AS
SELECT
    ROW_NUMBER() OVER (ORDER BY ep.id_encomenda, ep.id_produto) AS linha_id,
    ep.id_encomenda,
    ep.id_produto,
    p.nome  AS nome_produto,
    p.preco AS preco_produto,
    ep.quantidade
FROM Encomendas_Produtos ep
JOIN Produto p ON p.id_produto = ep.id_produto;


CREATE OR REPLACE VIEW vw_fornecedor_produtos AS
SELECT
    p.id_fornecedor,
    p.id_produto,
    p.nome,
    p.descricao,
    p.preco,
    p.stock,
    p.is_approved,
    p.estado_produto,
    tp.designacao AS tipo_designacao
FROM Produto p
LEFT JOIN Tipo_Produto tp ON tp.id_tipo_produto = p.id_tipo_produto;


CREATE OR REPLACE VIEW vw_conta_perfil AS
SELECT
    u.id_utilizador,
    u.nome,
    u.email,
    u.morada,
    u.nif,
    u.id_tipo_utilizador,
    tu.designacao AS tipo_designacao
FROM Utilizador u
LEFT JOIN Tipo_Utilizador tu ON tu.id_tipo_utilizador = u.id_tipo_utilizador;


CREATE OR REPLACE VIEW vw_conta_fornecedor_perfil AS
SELECT
    f.id_fornecedor,
    f.nome        AS fornecedor_nome,
    f.contacto,
    f.email       AS fornecedor_email,
    f.nif         AS fornecedor_nif,
    f.isSingular,
    f.morada      AS fornecedor_morada,
    f.imagem_fornecedor
FROM Fornecedor f;


CREATE OR REPLACE VIEW vw_fornecedor_encomendas AS
SELECT
    p.id_fornecedor,
    e.id_encomenda,
    e.data_encomenda,
    e.estado_encomenda,
    e.id_utilizador,
    u.nome  AS cliente_nome,
    u.email AS cliente_email,
    COALESCE(SUM(ep.quantidade * p.preco), 0) AS total_fornecedor
FROM Encomenda e
JOIN Encomendas_Produtos ep ON ep.id_encomenda = e.id_encomenda
JOIN Produto p ON p.id_produto = ep.id_produto
JOIN Utilizador u ON u.id_utilizador = e.id_utilizador
WHERE e.estado_encomenda <> 'Carrinho'
GROUP BY
    p.id_fornecedor,
    e.id_encomenda,
    e.data_encomenda,
    e.estado_encomenda,
    e.id_utilizador,
    u.nome,
    u.email;


CREATE OR REPLACE VIEW vw_fornecedor_encomenda_linhas AS
SELECT
    p.id_fornecedor,
    ep.id_encomenda,
    ep.id_produto,
    p.nome  AS nome_produto,
    p.preco AS preco_produto,
    ep.quantidade,
    (ep.quantidade * p.preco) AS subtotal
FROM Encomendas_Produtos ep
JOIN Produto p ON p.id_produto = ep.id_produto;
