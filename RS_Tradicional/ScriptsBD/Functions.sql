-- 03_functions.sql
-- =========================================
-- DROPs
-- =========================================

DROP FUNCTION IF EXISTS fn_total_encomenda(INT);
DROP FUNCTION IF EXISTS fn_stock_disponivel(INT);
DROP FUNCTION IF EXISTS fn_get_tipo_utilizador(INT);

-- =========================================
-- TOTAL DA ENCOMENDA
-- =========================================

CREATE OR REPLACE FUNCTION fn_total_encomenda(p_id_encomenda INT)
RETURNS NUMERIC(12,2)
LANGUAGE plpgsql
AS $$
DECLARE
    v_total NUMERIC(12,2) := 0;
BEGIN
    SELECT COALESCE(SUM(p.preco * ep.quantidade), 0)
    INTO v_total
    FROM encomendas_produtos ep
    JOIN produto p ON p.id_produto = ep.id_produto
    WHERE ep.id_encomenda = p_id_encomenda;

    RETURN v_total;
END;
$$;

-- =========================================
-- STOCK DISPONÍVEL
-- =========================================

CREATE OR REPLACE FUNCTION fn_stock_disponivel(p_id_produto INT)
RETURNS INT
LANGUAGE sql
AS $$
    SELECT stock
    FROM produto
    WHERE id_produto = p_id_produto;
$$;

-- =========================================
-- OBTÉM TIPO DE UTILIZADOR (em minúsculas)
-- =========================================

CREATE OR REPLACE FUNCTION fn_get_tipo_utilizador(p_id_utilizador INT)
RETURNS TEXT
LANGUAGE plpgsql
AS $$
DECLARE
    v_tipo TEXT;
BEGIN
    SELECT lower(tu.designacao)
    INTO v_tipo
    FROM utilizador u
    JOIN tipo_utilizador tu
      ON tu.id_tipo_utilizador = u.id_tipo_utilizador
    WHERE u.id_utilizador = p_id_utilizador;

    RETURN v_tipo;
END;
$$;
