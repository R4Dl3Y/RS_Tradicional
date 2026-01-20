-- 02_views.sql
-- =========================================
-- DROPs
-- =========================================

DROP VIEW IF EXISTS vw_produtos_publicos;
DROP VIEW IF EXISTS vw_produtos_admin;
DROP VIEW IF EXISTS vw_noticias_publicas;
DROP VIEW IF EXISTS vw_noticias_admin;
DROP VIEW IF EXISTS vw_encomendas_cliente;
DROP VIEW IF EXISTS vw_encomenda_linhas;

-- =========================================
-- LOJA: produtos aprovados e ativos
-- =========================================

CREATE OR REPLACE VIEW vw_produtos_publicos AS
SELECT
    p.id_produto,
    p.nome,
    p.descricao,
    p.preco,
    p.stock,
    p.estado_produto,
    p.is_approved,
    tp.designacao AS tipo_produto,
    f.nome        AS fornecedor_nome
FROM produto p
LEFT JOIN tipo_produto tp ON p.id_tipo_produto = tp.id_tipo_produto
LEFT JOIN fornecedor   f  ON p.id_fornecedor   = f.id_fornecedor
WHERE p.is_approved = TRUE
  AND p.estado_produto = 'Ativo';

GRANT SELECT ON vw_produtos_publicos
TO rs_cliente, rs_fornecedor, rs_gestor, rs_admin;

-- =========================================
-- Produtos (admin)
-- =========================================

CREATE OR REPLACE VIEW vw_produtos_admin AS
SELECT
    p.*,
    tp.designacao AS tipo_produto,
    f.nome        AS fornecedor_nome
FROM produto p
LEFT JOIN tipo_produto tp ON p.id_tipo_produto = tp.id_tipo_produto
LEFT JOIN fornecedor   f  ON p.id_fornecedor   = f.id_fornecedor;

GRANT SELECT ON vw_produtos_admin
TO rs_gestor, rs_admin;

-- =========================================
-- Notícias públicas
-- =========================================

CREATE OR REPLACE VIEW vw_noticias_publicas AS
SELECT
    n.id_noticia,
    n.titulo,
    n.conteudo,
    n.data_publicacao,
    tn.nome AS tipo_noticia,
    u.nome  AS autor_nome,
    u.email AS autor_email
FROM noticia n
LEFT JOIN tipo_noticia tn ON n.id_tipo_noticia = tn.id_tipo_noticia
LEFT JOIN utilizador   u  ON n.autor           = u.id_utilizador;

GRANT SELECT ON vw_noticias_publicas
TO rs_cliente, rs_fornecedor, rs_gestor, rs_admin;

-- =========================================
-- Notícias (admin)
-- =========================================

CREATE OR REPLACE VIEW vw_noticias_admin AS
SELECT
    n.*,
    tn.nome AS tipo_noticia,
    u.nome  AS autor_nome,
    u.email AS autor_email
FROM noticia n
LEFT JOIN tipo_noticia tn ON n.id_tipo_noticia = tn.id_tipo_noticia
LEFT JOIN utilizador   u  ON n.autor           = u.id_utilizador;

GRANT SELECT ON vw_noticias_admin
TO rs_gestor, rs_admin;

-- =========================================
-- Encomendas (cliente)
-- =========================================

CREATE OR REPLACE VIEW vw_encomendas_cliente AS
SELECT
    e.id_encomenda,
    e.data_encomenda,
    e.estado_encomenda,
    u.id_utilizador,
    u.nome  AS cliente_nome,
    u.email AS cliente_email
FROM encomenda e
JOIN utilizador u ON e.id_utilizador = u.id_utilizador;

GRANT SELECT ON vw_encomendas_cliente
TO rs_cliente, rs_fornecedor, rs_gestor, rs_admin;

-- =========================================
-- Linhas de encomenda
-- =========================================

CREATE OR REPLACE VIEW vw_encomenda_linhas AS
SELECT
    ep.id_encomenda,
    ep.id_produto,
    ep.quantidade,
    p.nome  AS produto_nome,
    p.preco AS produto_preco
FROM encomendas_produtos ep
JOIN produto p ON ep.id_produto = p.id_produto;

GRANT SELECT ON vw_encomenda_linhas
TO rs_cliente, rs_fornecedor, rs_gestor, rs_admin;
