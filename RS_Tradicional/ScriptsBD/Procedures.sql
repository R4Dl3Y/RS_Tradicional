-- 03_procedures.sql
-- Procedures principais de negócio (VERSÃO FIXED - com verificação de session/user_id via p_id_exec)

-- NOTA IMPORTANTE:
-- 1) Todas as operações "admin/gestor" agora exigem p_id_exec (id do utilizador logado).
-- 2) Isto implica ajustares as chamadas no Django para passar request.session["user_id"].
-- 3) Mantive nomes consistentes e criei ALIAS (wrappers) quando tinhas mismatch no Django (ex: aprovar/rejeitar produto).

-- ============================================================
-- UTILIZADORES
-- ============================================================

-- Registo de cliente via site (SEM p_id_exec)
DROP PROCEDURE IF EXISTS sp_registar_utilizador_cliente(TEXT, TEXT, TEXT, TEXT, TEXT);

CREATE OR REPLACE PROCEDURE sp_registar_utilizador_cliente(
    p_nome          TEXT,
    p_email         TEXT,
    p_password_hash TEXT,
    p_morada        TEXT,
    p_nif           TEXT
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_id_tipo_cliente INT;
BEGIN
    IF p_nome IS NULL OR btrim(p_nome) = '' THEN
        RAISE EXCEPTION 'O nome é obrigatório.';
    END IF;

    IF p_email IS NULL OR btrim(p_email) = '' THEN
        RAISE EXCEPTION 'O email é obrigatório.';
    END IF;

    IF p_password_hash IS NULL OR btrim(p_password_hash) = '' THEN
        RAISE EXCEPTION 'A password é obrigatória.';
    END IF;

    IF p_nif IS NULL OR p_nif !~ '^[0-9]{9}$' THEN
        RAISE EXCEPTION 'O NIF deve ter exatamente 9 dígitos.';
    END IF;

    IF EXISTS (SELECT 1 FROM Utilizador WHERE lower(email) = lower(p_email)) THEN
        RAISE EXCEPTION 'Já existe um utilizador com esse email.';
    END IF;

    IF EXISTS (SELECT 1 FROM Utilizador WHERE nif = p_nif) THEN
        RAISE EXCEPTION 'Já existe um utilizador com esse NIF.';
    END IF;

    SELECT id_tipo_utilizador
    INTO v_id_tipo_cliente
    FROM Tipo_Utilizador
    WHERE lower(designacao) = 'cliente'
    LIMIT 1;

    IF v_id_tipo_cliente IS NULL THEN
        RAISE EXCEPTION 'Tipo_Utilizador "cliente" não existe.';
    END IF;

    INSERT INTO Utilizador (nome, email, password, morada, nif, id_tipo_utilizador)
    VALUES (
        btrim(p_nome),
        btrim(p_email),
        p_password_hash,
        CASE WHEN p_morada IS NULL OR btrim(p_morada) = '' THEN NULL ELSE btrim(p_morada) END,
        p_nif,
        v_id_tipo_cliente
    );
END;
$$;


-- ============================================================
-- UTILIZADORES (ADMIN) - AGORA COM p_id_exec (ADMIN ONLY)
-- ============================================================

DROP PROCEDURE IF EXISTS sp_admin_utilizador_criar(INT, TEXT, TEXT, TEXT, TEXT, TEXT, INTEGER);

CREATE OR REPLACE PROCEDURE sp_admin_utilizador_criar(
    p_id_exec       INT,
    p_nome          TEXT,
    p_email         TEXT,
    p_password_hash TEXT,
    p_morada        TEXT,
    p_nif           TEXT,
    p_id_tipo       INTEGER
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_tipo_exec TEXT;
BEGIN
    v_tipo_exec := fn_get_tipo_utilizador(p_id_exec);
    IF v_tipo_exec IS NULL OR lower(v_tipo_exec) <> 'admin' THEN
        RAISE EXCEPTION 'Apenas administradores podem gerir utilizadores.';
    END IF;

    IF p_nome IS NULL OR btrim(p_nome) = '' THEN
        RAISE EXCEPTION 'O nome é obrigatório.';
    END IF;

    IF p_email IS NULL OR btrim(p_email) = '' THEN
        RAISE EXCEPTION 'O email é obrigatório.';
    END IF;

    IF p_password_hash IS NULL OR btrim(p_password_hash) = '' THEN
        RAISE EXCEPTION 'A password é obrigatória.';
    END IF;

    IF p_nif IS NULL OR p_nif !~ '^[0-9]{9}$' THEN
        RAISE EXCEPTION 'O NIF deve ter exatamente 9 dígitos.';
    END IF;

    IF p_id_tipo IS NOT NULL AND NOT EXISTS (
        SELECT 1 FROM Tipo_Utilizador WHERE id_tipo_utilizador = p_id_tipo
    ) THEN
        RAISE EXCEPTION 'Tipo de utilizador inválido.';
    END IF;

    IF EXISTS (SELECT 1 FROM Utilizador WHERE lower(email) = lower(p_email)) THEN
        RAISE EXCEPTION 'Já existe um utilizador com esse email.';
    END IF;

    IF EXISTS (SELECT 1 FROM Utilizador WHERE nif = p_nif) THEN
        RAISE EXCEPTION 'Já existe um utilizador com esse NIF.';
    END IF;

    INSERT INTO Utilizador (nome, email, password, morada, nif, id_tipo_utilizador)
    VALUES (
        btrim(p_nome),
        btrim(p_email),
        p_password_hash,
        CASE WHEN p_morada IS NULL OR btrim(p_morada) = '' THEN NULL ELSE btrim(p_morada) END,
        p_nif,
        p_id_tipo
    );
END;
$$;


DROP PROCEDURE IF EXISTS sp_admin_utilizador_atualizar(INT, INT, TEXT, TEXT, TEXT, TEXT, TEXT, INT);

CREATE OR REPLACE PROCEDURE sp_admin_utilizador_atualizar(
    p_id_exec       INT,
    p_id_utilizador INT,
    p_nome          TEXT,
    p_email         TEXT,
    p_password_hash TEXT,   -- pode vir NULL / string vazia para manter
    p_morada        TEXT,
    p_nif           TEXT,
    p_id_tipo       INT
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_tipo_exec TEXT;
BEGIN
    v_tipo_exec := fn_get_tipo_utilizador(p_id_exec);
    IF v_tipo_exec IS NULL OR lower(v_tipo_exec) <> 'admin' THEN
        RAISE EXCEPTION 'Apenas administradores podem gerir utilizadores.';
    END IF;

    IF NOT EXISTS (SELECT 1 FROM Utilizador WHERE id_utilizador = p_id_utilizador) THEN
        RAISE EXCEPTION 'Utilizador com id % não existe.', p_id_utilizador;
    END IF;

    IF p_nome IS NULL OR btrim(p_nome) = '' THEN
        RAISE EXCEPTION 'O nome é obrigatório.';
    END IF;

    IF p_email IS NULL OR btrim(p_email) = '' THEN
        RAISE EXCEPTION 'O email é obrigatório.';
    END IF;

    IF p_nif IS NULL OR p_nif !~ '^[0-9]{9}$' THEN
        RAISE EXCEPTION 'O NIF deve ter exatamente 9 dígitos.';
    END IF;

    IF p_id_tipo IS NOT NULL AND NOT EXISTS (
        SELECT 1 FROM Tipo_Utilizador WHERE id_tipo_utilizador = p_id_tipo
    ) THEN
        RAISE EXCEPTION 'Tipo de utilizador inválido.';
    END IF;

    IF EXISTS (
        SELECT 1 FROM Utilizador
        WHERE lower(email) = lower(p_email)
          AND id_utilizador <> p_id_utilizador
    ) THEN
        RAISE EXCEPTION 'Já existe outro utilizador com esse email.';
    END IF;

    IF EXISTS (
        SELECT 1 FROM Utilizador
        WHERE nif = p_nif
          AND id_utilizador <> p_id_utilizador
    ) THEN
        RAISE EXCEPTION 'Já existe outro utilizador com esse NIF.';
    END IF;

    UPDATE Utilizador
    SET
        nome   = btrim(p_nome),
        email  = btrim(p_email),
        morada = CASE WHEN p_morada IS NULL OR btrim(p_morada) = '' THEN NULL ELSE btrim(p_morada) END,
        nif    = p_nif,
        id_tipo_utilizador = p_id_tipo,
        password = COALESCE(
            NULLIF(COALESCE(btrim(p_password_hash), ''), ''),
            password
        )
    WHERE id_utilizador = p_id_utilizador;
END;
$$;


DROP PROCEDURE IF EXISTS sp_admin_utilizador_apagar(INT, INT);

CREATE OR REPLACE PROCEDURE sp_admin_utilizador_apagar(
    p_id_exec       INT,
    p_id_utilizador INT
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_tipo_exec TEXT;
BEGIN
    v_tipo_exec := fn_get_tipo_utilizador(p_id_exec);
    IF v_tipo_exec IS NULL OR lower(v_tipo_exec) <> 'admin' THEN
        RAISE EXCEPTION 'Apenas administradores podem gerir utilizadores.';
    END IF;

    IF NOT EXISTS (SELECT 1 FROM Utilizador WHERE id_utilizador = p_id_utilizador) THEN
        RAISE EXCEPTION 'Utilizador com id % não existe.', p_id_utilizador;
    END IF;

    DELETE FROM Utilizador
    WHERE id_utilizador = p_id_utilizador;
END;
$$;


-- ============================================================
-- TIPO_UTILIZADOR (ADMIN) - JÁ TINHA p_id_exec (mantido)
-- ============================================================

DROP PROCEDURE IF EXISTS sp_tipo_utilizador_criar(INT, TEXT);

CREATE OR REPLACE PROCEDURE sp_tipo_utilizador_criar(
    p_id_exec    INT,
    p_designacao TEXT
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_tipo_exec TEXT;
BEGIN
    v_tipo_exec := fn_get_tipo_utilizador(p_id_exec);
    IF v_tipo_exec IS NULL OR lower(v_tipo_exec) <> 'admin' THEN
        RAISE EXCEPTION 'Apenas administradores podem gerir tipos de utilizador.';
    END IF;

    IF p_designacao IS NULL OR btrim(p_designacao) = '' THEN
        RAISE EXCEPTION 'A designação é obrigatória.';
    END IF;

    IF EXISTS (
        SELECT 1 FROM Tipo_Utilizador
        WHERE lower(designacao) = lower(p_designacao)
    ) THEN
        RAISE EXCEPTION 'Já existe um tipo de utilizador com essa designação.';
    END IF;

    INSERT INTO Tipo_Utilizador (designacao)
    VALUES (btrim(p_designacao));
END;
$$;


DROP PROCEDURE IF EXISTS sp_tipo_utilizador_atualizar(INT, INT, TEXT);

CREATE OR REPLACE PROCEDURE sp_tipo_utilizador_atualizar(
    p_id_exec            INT,
    p_id_tipo_utilizador INT,
    p_designacao         TEXT
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_tipo_exec TEXT;
BEGIN
    v_tipo_exec := fn_get_tipo_utilizador(p_id_exec);
    IF v_tipo_exec IS NULL OR lower(v_tipo_exec) <> 'admin' THEN
        RAISE EXCEPTION 'Apenas administradores podem gerir tipos de utilizador.';
    END IF;

    IF NOT EXISTS (SELECT 1 FROM Tipo_Utilizador WHERE id_tipo_utilizador = p_id_tipo_utilizador) THEN
        RAISE EXCEPTION 'Tipo_Utilizador com id % não existe.', p_id_tipo_utilizador;
    END IF;

    IF p_designacao IS NULL OR btrim(p_designacao) = '' THEN
        RAISE EXCEPTION 'A designação é obrigatória.';
    END IF;

    IF EXISTS (
        SELECT 1 FROM Tipo_Utilizador
        WHERE lower(designacao) = lower(p_designacao)
          AND id_tipo_utilizador <> p_id_tipo_utilizador
    ) THEN
        RAISE EXCEPTION 'Já existe outro tipo de utilizador com essa designação.';
    END IF;

    UPDATE Tipo_Utilizador
    SET designacao = btrim(p_designacao)
    WHERE id_tipo_utilizador = p_id_tipo_utilizador;
END;
$$;


DROP PROCEDURE IF EXISTS sp_tipo_utilizador_apagar(INT, INT);

CREATE OR REPLACE PROCEDURE sp_tipo_utilizador_apagar(
    p_id_exec            INT,
    p_id_tipo_utilizador INT
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_tipo_exec TEXT;
BEGIN
    v_tipo_exec := fn_get_tipo_utilizador(p_id_exec);
    IF v_tipo_exec IS NULL OR lower(v_tipo_exec) <> 'admin' THEN
        RAISE EXCEPTION 'Apenas administradores podem gerir tipos de utilizador.';
    END IF;

    IF NOT EXISTS (SELECT 1 FROM Tipo_Utilizador WHERE id_tipo_utilizador = p_id_tipo_utilizador) THEN
        RAISE EXCEPTION 'Tipo_Utilizador com id % não existe.', p_id_tipo_utilizador;
    END IF;

    DELETE FROM Tipo_Utilizador
    WHERE id_tipo_utilizador = p_id_tipo_utilizador;
END;
$$;


-- ============================================================
-- TIPO_PRODUTO (ADMIN/GESTOR) - AGORA COM p_id_exec
-- ============================================================

DROP PROCEDURE IF EXISTS sp_admin_tipo_produto_criar(INT, TEXT);

CREATE OR REPLACE PROCEDURE sp_admin_tipo_produto_criar(
    p_id_exec    INT,
    p_designacao TEXT
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_tipo_exec TEXT;
BEGIN
    v_tipo_exec := fn_get_tipo_utilizador(p_id_exec);
    IF v_tipo_exec IS NULL OR lower(v_tipo_exec) NOT IN ('admin','gestor') THEN
        RAISE EXCEPTION 'Apenas admin/gestor podem gerir tipos de produto.';
    END IF;

    IF p_designacao IS NULL OR btrim(p_designacao) = '' THEN
        RAISE EXCEPTION 'A designação é obrigatória.';
    END IF;

    IF EXISTS (
        SELECT 1 FROM Tipo_Produto
        WHERE lower(designacao) = lower(btrim(p_designacao))
    ) THEN
        RAISE EXCEPTION 'Já existe um tipo de produto com essa designação.';
    END IF;

    INSERT INTO Tipo_Produto(designacao)
    VALUES (btrim(p_designacao));
END;
$$;


DROP PROCEDURE IF EXISTS sp_admin_tipo_produto_atualizar(INT, INT, TEXT);

CREATE OR REPLACE PROCEDURE sp_admin_tipo_produto_atualizar(
    p_id_exec         INT,
    p_id_tipo_produto INT,
    p_designacao      TEXT
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_tipo_exec TEXT;
BEGIN
    v_tipo_exec := fn_get_tipo_utilizador(p_id_exec);
    IF v_tipo_exec IS NULL OR lower(v_tipo_exec) NOT IN ('admin','gestor') THEN
        RAISE EXCEPTION 'Apenas admin/gestor podem gerir tipos de produto.';
    END IF;

    IF NOT EXISTS (SELECT 1 FROM Tipo_Produto WHERE id_tipo_produto = p_id_tipo_produto) THEN
        RAISE EXCEPTION 'Tipo_Produto com id % não existe.', p_id_tipo_produto;
    END IF;

    IF p_designacao IS NULL OR btrim(p_designacao) = '' THEN
        RAISE EXCEPTION 'A designação é obrigatória.';
    END IF;

    IF EXISTS (
        SELECT 1 FROM Tipo_Produto
        WHERE lower(designacao) = lower(btrim(p_designacao))
          AND id_tipo_produto <> p_id_tipo_produto
    ) THEN
        RAISE EXCEPTION 'Já existe outro tipo de produto com essa designação.';
    END IF;

    UPDATE Tipo_Produto
    SET designacao = btrim(p_designacao)
    WHERE id_tipo_produto = p_id_tipo_produto;
END;
$$;


DROP PROCEDURE IF EXISTS sp_admin_tipo_produto_apagar(INT, INT);

CREATE OR REPLACE PROCEDURE sp_admin_tipo_produto_apagar(
    p_id_exec         INT,
    p_id_tipo_produto INT
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_tipo_exec TEXT;
BEGIN
    v_tipo_exec := fn_get_tipo_utilizador(p_id_exec);
    IF v_tipo_exec IS NULL OR lower(v_tipo_exec) NOT IN ('admin','gestor') THEN
        RAISE EXCEPTION 'Apenas admin/gestor podem gerir tipos de produto.';
    END IF;

    IF NOT EXISTS (SELECT 1 FROM Tipo_Produto WHERE id_tipo_produto = p_id_tipo_produto) THEN
        RAISE EXCEPTION 'Tipo_Produto com id % não existe.', p_id_tipo_produto;
    END IF;

    IF EXISTS (SELECT 1 FROM Produto WHERE id_tipo_produto = p_id_tipo_produto) THEN
        RAISE EXCEPTION 'Não é possível apagar: existem produtos associados.';
    END IF;

    DELETE FROM Tipo_Produto
    WHERE id_tipo_produto = p_id_tipo_produto;
END;
$$;


-- ============================================================
-- FORNECEDOR (ADMIN/GESTOR) - JÁ TINHA p_id_exec (mantido)
-- + ALIAS "sp_admin_fornecedor_*" para bater com Django (se usares esses nomes)
-- ============================================================

DROP PROCEDURE IF EXISTS sp_fornecedor_criar(INT, TEXT, TEXT, TEXT, TEXT, BOOLEAN, TEXT, TEXT);

CREATE OR REPLACE PROCEDURE sp_fornecedor_criar(
    p_id_exec           INT,
    p_nome              TEXT,
    p_contacto          TEXT,
    p_email             TEXT,
    p_nif               TEXT,
    p_is_singular       BOOLEAN,
    p_morada            TEXT,
    p_imagem_fornecedor TEXT
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_tipo_exec TEXT;
BEGIN
    v_tipo_exec := fn_get_tipo_utilizador(p_id_exec);
    IF v_tipo_exec IS NULL OR lower(v_tipo_exec) NOT IN ('admin','gestor') THEN
        RAISE EXCEPTION 'Apenas admin/gestor podem gerir fornecedores.';
    END IF;

    IF p_nome IS NULL OR btrim(p_nome) = '' THEN
        RAISE EXCEPTION 'O nome do fornecedor é obrigatório.';
    END IF;

    IF p_contacto IS NULL OR btrim(p_contacto) = '' THEN
        RAISE EXCEPTION 'O contacto do fornecedor é obrigatório.';
    END IF;

    IF p_email IS NULL OR btrim(p_email) = '' THEN
        RAISE EXCEPTION 'O email do fornecedor é obrigatório.';
    END IF;

    IF p_nif IS NULL OR p_nif !~ '^[0-9]{9}$' THEN
        RAISE EXCEPTION 'O NIF do fornecedor deve ter exatamente 9 dígitos.';
    END IF;

    IF (NOT p_is_singular) AND (p_morada IS NULL OR btrim(p_morada) = '') THEN
        RAISE EXCEPTION 'Para fornecedores não singulares, a morada é obrigatória.';
    END IF;

    IF EXISTS (SELECT 1 FROM Fornecedor WHERE lower(email) = lower(p_email)) THEN
        RAISE EXCEPTION 'Já existe um fornecedor com esse email.';
    END IF;

    IF EXISTS (SELECT 1 FROM Fornecedor WHERE nif = p_nif) THEN
        RAISE EXCEPTION 'Já existe um fornecedor com esse NIF.';
    END IF;

    INSERT INTO Fornecedor(nome, contacto, email, nif, isSingular, morada, imagem_fornecedor)
    VALUES(
        btrim(p_nome),
        btrim(p_contacto),
        btrim(p_email),
        p_nif,
        p_is_singular,
        CASE WHEN p_morada IS NULL OR btrim(p_morada) = '' THEN NULL ELSE btrim(p_morada) END,
        CASE WHEN p_imagem_fornecedor IS NULL OR btrim(p_imagem_fornecedor) = '' THEN NULL ELSE btrim(p_imagem_fornecedor) END
    );
END;
$$;


DROP PROCEDURE IF EXISTS sp_fornecedor_atualizar(INT, INT, TEXT, TEXT, TEXT, TEXT, BOOLEAN, TEXT, TEXT);

CREATE OR REPLACE PROCEDURE sp_fornecedor_atualizar(
    p_id_exec           INT,
    p_id_fornecedor     INT,
    p_nome              TEXT,
    p_contacto          TEXT,
    p_email             TEXT,
    p_nif               TEXT,
    p_is_singular       BOOLEAN,
    p_morada            TEXT,
    p_imagem_fornecedor TEXT
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_tipo_exec TEXT;
BEGIN
    v_tipo_exec := fn_get_tipo_utilizador(p_id_exec);
    IF v_tipo_exec IS NULL OR lower(v_tipo_exec) NOT IN ('admin','gestor') THEN
        RAISE EXCEPTION 'Apenas admin/gestor podem gerir fornecedores.';
    END IF;

    IF NOT EXISTS (SELECT 1 FROM Fornecedor WHERE id_fornecedor = p_id_fornecedor) THEN
        RAISE EXCEPTION 'Fornecedor com id % não existe.', p_id_fornecedor;
    END IF;

    IF p_nome IS NULL OR btrim(p_nome) = '' THEN
        RAISE EXCEPTION 'O nome do fornecedor é obrigatório.';
    END IF;

    IF p_contacto IS NULL OR btrim(p_contacto) = '' THEN
        RAISE EXCEPTION 'O contacto do fornecedor é obrigatório.';
    END IF;

    IF p_email IS NULL OR btrim(p_email) = '' THEN
        RAISE EXCEPTION 'O email do fornecedor é obrigatório.';
    END IF;

    IF p_nif IS NULL OR p_nif !~ '^[0-9]{9}$' THEN
        RAISE EXCEPTION 'O NIF do fornecedor deve ter exatamente 9 dígitos.';
    END IF;

    IF (NOT p_is_singular) AND (p_morada IS NULL OR btrim(p_morada) = '') THEN
        RAISE EXCEPTION 'Para fornecedores não singulares, a morada é obrigatória.';
    END IF;

    IF EXISTS (
        SELECT 1 FROM Fornecedor
        WHERE lower(email) = lower(p_email)
          AND id_fornecedor <> p_id_fornecedor
    ) THEN
        RAISE EXCEPTION 'Já existe outro fornecedor com esse email.';
    END IF;

    IF EXISTS (
        SELECT 1 FROM Fornecedor
        WHERE nif = p_nif
          AND id_fornecedor <> p_id_fornecedor
    ) THEN
        RAISE EXCEPTION 'Já existe outro fornecedor com esse NIF.';
    END IF;

    UPDATE Fornecedor
    SET
        nome              = btrim(p_nome),
        contacto          = btrim(p_contacto),
        email             = btrim(p_email),
        nif               = p_nif,
        isSingular        = p_is_singular,
        morada            = CASE WHEN p_morada IS NULL OR btrim(p_morada) = '' THEN NULL ELSE btrim(p_morada) END,
        imagem_fornecedor = CASE WHEN p_imagem_fornecedor IS NULL OR btrim(p_imagem_fornecedor) = '' THEN NULL ELSE btrim(p_imagem_fornecedor) END
    WHERE id_fornecedor = p_id_fornecedor;
END;
$$;


DROP PROCEDURE IF EXISTS sp_fornecedor_apagar(INT, INT);

CREATE OR REPLACE PROCEDURE sp_fornecedor_apagar(
    p_id_exec       INT,
    p_id_fornecedor INT
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_tipo_exec TEXT;
BEGIN
    v_tipo_exec := fn_get_tipo_utilizador(p_id_exec);
    IF v_tipo_exec IS NULL OR lower(v_tipo_exec) NOT IN ('admin','gestor') THEN
        RAISE EXCEPTION 'Apenas admin/gestor podem gerir fornecedores.';
    END IF;

    IF NOT EXISTS (SELECT 1 FROM Fornecedor WHERE id_fornecedor = p_id_fornecedor) THEN
        RAISE EXCEPTION 'Fornecedor com id % não existe.', p_id_fornecedor;
    END IF;

    DELETE FROM Fornecedor
    WHERE id_fornecedor = p_id_fornecedor;
END;
$$;

-- ALIAS para bater com nomes "sp_admin_fornecedor_*"
DROP PROCEDURE IF EXISTS sp_admin_fornecedor_criar(INT, TEXT, TEXT, TEXT, TEXT, BOOLEAN, TEXT, TEXT);
CREATE OR REPLACE PROCEDURE sp_admin_fornecedor_criar(
    p_id_exec           INT,
    p_nome              TEXT,
    p_contacto          TEXT,
    p_email             TEXT,
    p_nif               TEXT,
    p_is_singular       BOOLEAN,
    p_morada            TEXT,
    p_imagem_fornecedor TEXT
)
LANGUAGE plpgsql
AS $$
BEGIN
    CALL sp_fornecedor_criar(p_id_exec, p_nome, p_contacto, p_email, p_nif, p_is_singular, p_morada, p_imagem_fornecedor);
END;
$$;

DROP PROCEDURE IF EXISTS sp_admin_fornecedor_atualizar(INT, INT, TEXT, TEXT, TEXT, TEXT, BOOLEAN, TEXT, TEXT);
CREATE OR REPLACE PROCEDURE sp_admin_fornecedor_atualizar(
    p_id_exec           INT,
    p_id_fornecedor     INT,
    p_nome              TEXT,
    p_contacto          TEXT,
    p_email             TEXT,
    p_nif               TEXT,
    p_is_singular       BOOLEAN,
    p_morada            TEXT,
    p_imagem_fornecedor TEXT
)
LANGUAGE plpgsql
AS $$
BEGIN
    CALL sp_fornecedor_atualizar(p_id_exec, p_id_fornecedor, p_nome, p_contacto, p_email, p_nif, p_is_singular, p_morada, p_imagem_fornecedor);
END;
$$;

DROP PROCEDURE IF EXISTS sp_admin_fornecedor_apagar(INT, INT);
CREATE OR REPLACE PROCEDURE sp_admin_fornecedor_apagar(
    p_id_exec       INT,
    p_id_fornecedor INT
)
LANGUAGE plpgsql
AS $$
BEGIN
    CALL sp_fornecedor_apagar(p_id_exec, p_id_fornecedor);
END;
$$;


-- ============================================================
-- PRODUTO (ADMIN/GESTOR) - AGORA COM p_id_exec
-- ============================================================

DROP PROCEDURE IF EXISTS sp_admin_produto_criar(INT, TEXT, TEXT, NUMERIC, INT, TEXT, BOOLEAN, INT, INT);

CREATE OR REPLACE PROCEDURE sp_admin_produto_criar(
    p_id_exec         INT,
    p_nome            TEXT,
    p_descricao       TEXT,
    p_preco           NUMERIC,
    p_stock           INT,
    p_estado_produto  TEXT,
    p_is_approved     BOOLEAN,
    p_id_tipo_produto INT,
    p_id_fornecedor   INT
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_tipo_exec TEXT;
BEGIN
    v_tipo_exec := fn_get_tipo_utilizador(p_id_exec);
    IF v_tipo_exec IS NULL OR lower(v_tipo_exec) NOT IN ('admin','gestor') THEN
        RAISE EXCEPTION 'Apenas admin/gestor podem gerir produtos.';
    END IF;

    IF p_nome IS NULL OR btrim(p_nome) = '' THEN
        RAISE EXCEPTION 'O nome do produto é obrigatório.';
    END IF;

    IF p_preco IS NULL OR p_preco < 0 THEN
        RAISE EXCEPTION 'Preço inválido.';
    END IF;

    IF p_stock IS NULL OR p_stock < 0 THEN
        RAISE EXCEPTION 'Stock inválido.';
    END IF;

    IF p_id_tipo_produto IS NOT NULL AND NOT EXISTS (
        SELECT 1 FROM Tipo_Produto WHERE id_tipo_produto = p_id_tipo_produto
    ) THEN
        RAISE EXCEPTION 'Tipo de produto inválido.';
    END IF;

    IF p_id_fornecedor IS NOT NULL AND NOT EXISTS (
        SELECT 1 FROM Fornecedor WHERE id_fornecedor = p_id_fornecedor
    ) THEN
        RAISE EXCEPTION 'Fornecedor inválido.';
    END IF;

    INSERT INTO Produto(
        nome, descricao, preco, stock,
        is_approved, estado_produto,
        id_tipo_produto, id_fornecedor
    )
    VALUES(
        btrim(p_nome),
        CASE WHEN p_descricao IS NULL OR btrim(p_descricao) = '' THEN NULL ELSE p_descricao END,
        p_preco,
        p_stock,
        COALESCE(p_is_approved, FALSE),
        COALESCE(NULLIF(btrim(p_estado_produto), ''), 'Ativo'),
        p_id_tipo_produto,
        p_id_fornecedor
    );
END;
$$;


DROP PROCEDURE IF EXISTS sp_admin_produto_atualizar(INT, INT, TEXT, TEXT, NUMERIC, INT, TEXT, BOOLEAN, INT, INT);

CREATE OR REPLACE PROCEDURE sp_admin_produto_atualizar(
    p_id_exec         INT,
    p_id_produto      INT,
    p_nome            TEXT,
    p_descricao       TEXT,
    p_preco           NUMERIC,
    p_stock           INT,
    p_estado_produto  TEXT,
    p_is_approved     BOOLEAN,
    p_id_tipo_produto INT,
    p_id_fornecedor   INT
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_tipo_exec TEXT;
BEGIN
    v_tipo_exec := fn_get_tipo_utilizador(p_id_exec);
    IF v_tipo_exec IS NULL OR lower(v_tipo_exec) NOT IN ('admin','gestor') THEN
        RAISE EXCEPTION 'Apenas admin/gestor podem gerir produtos.';
    END IF;

    IF NOT EXISTS (SELECT 1 FROM Produto WHERE id_produto = p_id_produto) THEN
        RAISE EXCEPTION 'Produto com id % não existe.', p_id_produto;
    END IF;

    IF p_nome IS NULL OR btrim(p_nome) = '' THEN
        RAISE EXCEPTION 'O nome do produto é obrigatório.';
    END IF;

    IF p_preco IS NULL OR p_preco < 0 THEN
        RAISE EXCEPTION 'Preço inválido.';
    END IF;

    IF p_stock IS NULL OR p_stock < 0 THEN
        RAISE EXCEPTION 'Stock inválido.';
    END IF;

    IF p_id_tipo_produto IS NOT NULL AND NOT EXISTS (
        SELECT 1 FROM Tipo_Produto WHERE id_tipo_produto = p_id_tipo_produto
    ) THEN
        RAISE EXCEPTION 'Tipo de produto inválido.';
    END IF;

    IF p_id_fornecedor IS NOT NULL AND NOT EXISTS (
        SELECT 1 FROM Fornecedor WHERE id_fornecedor = p_id_fornecedor
    ) THEN
        RAISE EXCEPTION 'Fornecedor inválido.';
    END IF;

    UPDATE Produto
    SET
        nome            = btrim(p_nome),
        descricao       = CASE WHEN p_descricao IS NULL OR btrim(p_descricao) = '' THEN NULL ELSE p_descricao END,
        preco           = p_preco,
        stock           = p_stock,
        is_approved     = COALESCE(p_is_approved, FALSE),
        estado_produto  = COALESCE(NULLIF(btrim(p_estado_produto), ''), 'Ativo'),
        id_tipo_produto = p_id_tipo_produto,
        id_fornecedor   = p_id_fornecedor
    WHERE id_produto = p_id_produto;
END;
$$;


DROP PROCEDURE IF EXISTS sp_admin_produto_apagar(INT, INT);

CREATE OR REPLACE PROCEDURE sp_admin_produto_apagar(
    p_id_exec   INT,
    p_id_produto INT
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_tipo_exec TEXT;
BEGIN
    v_tipo_exec := fn_get_tipo_utilizador(p_id_exec);
    IF v_tipo_exec IS NULL OR lower(v_tipo_exec) NOT IN ('admin','gestor') THEN
        RAISE EXCEPTION 'Apenas admin/gestor podem gerir produtos.';
    END IF;

    IF NOT EXISTS (SELECT 1 FROM Produto WHERE id_produto = p_id_produto) THEN
        RAISE EXCEPTION 'Produto com id % não existe.', p_id_produto;
    END IF;

    DELETE FROM Produto
    WHERE id_produto = p_id_produto;
END;
$$;


-- Fornecedor submete produto (PENDENTE) - já usa p_id_exec e valida "fornecedor"
DROP PROCEDURE IF EXISTS sp_fornecedor_submeter_produto(INT, TEXT, TEXT, NUMERIC, INT, INT);

CREATE OR REPLACE PROCEDURE sp_fornecedor_submeter_produto(
    p_id_exec         INT,
    p_nome            TEXT,
    p_descricao       TEXT,
    p_preco           NUMERIC,
    p_stock           INT,
    p_id_tipo_produto INT
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_tipo_exec   TEXT;
    v_email_exec  TEXT;
    v_id_fornec   INT;
BEGIN
    v_tipo_exec := fn_get_tipo_utilizador(p_id_exec);
    IF v_tipo_exec IS NULL OR lower(v_tipo_exec) <> 'fornecedor' THEN
        RAISE EXCEPTION 'Apenas utilizadores do tipo Fornecedor podem submeter produtos.';
    END IF;

    SELECT email INTO v_email_exec
    FROM Utilizador
    WHERE id_utilizador = p_id_exec;

    SELECT id_fornecedor
    INTO v_id_fornec
    FROM Fornecedor
    WHERE lower(email) = lower(v_email_exec)
    LIMIT 1;

    IF v_id_fornec IS NULL THEN
        RAISE EXCEPTION 'Não foi encontrado fornecedor associado ao email do utilizador.';
    END IF;

    IF p_nome IS NULL OR btrim(p_nome) = '' THEN
        RAISE EXCEPTION 'O nome do produto é obrigatório.';
    END IF;

    IF p_preco IS NULL OR p_preco < 0 THEN
        RAISE EXCEPTION 'Preço inválido.';
    END IF;

    IF p_stock IS NULL OR p_stock < 0 THEN
        RAISE EXCEPTION 'Stock inválido.';
    END IF;

    IF p_id_tipo_produto IS NOT NULL AND NOT EXISTS (
        SELECT 1 FROM Tipo_Produto WHERE id_tipo_produto = p_id_tipo_produto
    ) THEN
        RAISE EXCEPTION 'Tipo de produto inválido.';
    END IF;

    INSERT INTO Produto(
        nome, descricao, preco, stock,
        is_approved, estado_produto,
        id_tipo_produto, id_fornecedor
    )
    VALUES(
        btrim(p_nome),
        CASE WHEN p_descricao IS NULL OR btrim(p_descricao) = '' THEN NULL ELSE p_descricao END,
        p_preco,
        p_stock,
        FALSE,
        'Pendente',
        p_id_tipo_produto,
        v_id_fornec
    );
END;
$$;


-- Aprovar / Rejeitar produto (admin/gestor) - já tinha p_id_exec (mantido)
DROP PROCEDURE IF EXISTS sp_admin_produto_aprovar(INT, INT);

CREATE OR REPLACE PROCEDURE sp_admin_produto_aprovar(
    p_id_exec    INT,
    p_id_produto INT
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_tipo_exec TEXT;
    v_estado    TEXT;
BEGIN
    v_tipo_exec := fn_get_tipo_utilizador(p_id_exec);
    IF v_tipo_exec IS NULL OR lower(v_tipo_exec) NOT IN ('admin','gestor') THEN
        RAISE EXCEPTION 'Apenas admin/gestor podem aprovar produtos.';
    END IF;

    SELECT estado_produto
    INTO v_estado
    FROM Produto
    WHERE id_produto = p_id_produto;

    IF v_estado IS NULL THEN
        RAISE EXCEPTION 'Produto com id % não existe.', p_id_produto;
    END IF;

    UPDATE Produto
    SET
        is_approved    = TRUE,
        estado_produto = CASE WHEN lower(estado_produto) = 'pendente' THEN 'Ativo' ELSE estado_produto END
    WHERE id_produto = p_id_produto;
END;
$$;


DROP PROCEDURE IF EXISTS sp_admin_produto_rejeitar(INT, INT);

CREATE OR REPLACE PROCEDURE sp_admin_produto_rejeitar(
    p_id_exec    INT,
    p_id_produto INT
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_tipo_exec TEXT;
BEGIN
    v_tipo_exec := fn_get_tipo_utilizador(p_id_exec);
    IF v_tipo_exec IS NULL OR lower(v_tipo_exec) NOT IN ('admin','gestor') THEN
        RAISE EXCEPTION 'Apenas admin/gestor podem rejeitar produtos.';
    END IF;

    IF NOT EXISTS (SELECT 1 FROM Produto WHERE id_produto = p_id_produto) THEN
        RAISE EXCEPTION 'Produto com id % não existe.', p_id_produto;
    END IF;

    UPDATE Produto
    SET
        is_approved    = FALSE,
        estado_produto = 'Rejeitado'
    WHERE id_produto = p_id_produto;
END;
$$;

-- ALIAS para bater com nomes que tinhas no Django (sp_admin_aprovar_produto / sp_admin_rejeitar_produto)
DROP PROCEDURE IF EXISTS sp_admin_aprovar_produto(INT, INT);
CREATE OR REPLACE PROCEDURE sp_admin_aprovar_produto(p_id_exec INT, p_id_produto INT)
LANGUAGE plpgsql
AS $$
BEGIN
    CALL sp_admin_produto_aprovar(p_id_exec, p_id_produto);
END;
$$;

DROP PROCEDURE IF EXISTS sp_admin_rejeitar_produto(INT, INT);
CREATE OR REPLACE PROCEDURE sp_admin_rejeitar_produto(p_id_exec INT, p_id_produto INT)
LANGUAGE plpgsql
AS $$
BEGIN
    CALL sp_admin_produto_rejeitar(p_id_exec, p_id_produto);
END;
$$;


-- ============================================================
-- ENCOMENDAS & LOJA
-- ============================================================

-- Loja: adicionar produto ao Carrinho (valida "cliente" pelo próprio id)
DROP PROCEDURE IF EXISTS sp_loja_adicionar_produto(INT, INT, INT);

CREATE OR REPLACE PROCEDURE sp_loja_adicionar_produto(
    p_id_utilizador INT,
    p_id_produto    INT,
    p_quantidade    INT
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_tipo_cliente TEXT;
    v_encomenda_id INT;
    v_stock        INT;
    v_qtd_atual    INT;
BEGIN
    v_tipo_cliente := fn_get_tipo_utilizador(p_id_utilizador);
    IF v_tipo_cliente IS NULL OR lower(v_tipo_cliente) <> 'cliente' THEN
        RAISE EXCEPTION 'Apenas clientes podem usar o carrinho.';
    END IF;

    IF p_quantidade <= 0 THEN
        RAISE EXCEPTION 'Quantidade inválida (%).', p_quantidade;
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM Produto
        WHERE id_produto = p_id_produto
          AND is_approved = TRUE
          AND estado_produto = 'Ativo'
    ) THEN
        RAISE EXCEPTION 'Produto inválido ou inativo (%).', p_id_produto;
    END IF;

    SELECT stock
    INTO v_stock
    FROM Produto
    WHERE id_produto = p_id_produto;

    IF v_stock IS NULL OR v_stock < 0 THEN
        RAISE EXCEPTION 'Stock inválido para produto %.', p_id_produto;
    END IF;

    SELECT id_encomenda
    INTO v_encomenda_id
    FROM Encomenda
    WHERE id_utilizador = p_id_utilizador
      AND estado_encomenda = 'Carrinho'
    LIMIT 1;

    IF v_encomenda_id IS NULL THEN
        INSERT INTO Encomenda (data_encomenda, id_utilizador, estado_encomenda)
        VALUES (CURRENT_DATE, p_id_utilizador, 'Carrinho')
        RETURNING id_encomenda INTO v_encomenda_id;
    END IF;

    SELECT quantidade
    INTO v_qtd_atual
    FROM Encomendas_Produtos
    WHERE id_encomenda = v_encomenda_id
      AND id_produto   = p_id_produto;

    v_qtd_atual := COALESCE(v_qtd_atual, 0);

    IF v_qtd_atual + p_quantidade > v_stock THEN
        RAISE EXCEPTION
            'Quantidade total (% + %) excede o stock disponível (%) para o produto %.',
            v_qtd_atual, p_quantidade, v_stock, p_id_produto;
    END IF;

    INSERT INTO Encomendas_Produtos (id_encomenda, id_produto, quantidade)
    VALUES (v_encomenda_id, p_id_produto, p_quantidade)
    ON CONFLICT (id_encomenda, id_produto)
    DO UPDATE SET quantidade = Encomendas_Produtos.quantidade + EXCLUDED.quantidade;
END;
$$;


-- Loja: finalizar encomenda (Carrinho -> Pendente)
DROP PROCEDURE IF EXISTS sp_loja_finalizar_encomenda(INT);

CREATE OR REPLACE PROCEDURE sp_loja_finalizar_encomenda(
    p_id_utilizador INT
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_tipo_cliente TEXT;
    v_encomenda_id INT;
BEGIN
    v_tipo_cliente := fn_get_tipo_utilizador(p_id_utilizador);
    IF v_tipo_cliente IS NULL OR lower(v_tipo_cliente) <> 'cliente' THEN
        RAISE EXCEPTION 'Apenas clientes podem finalizar encomendas.';
    END IF;

    SELECT id_encomenda
    INTO v_encomenda_id
    FROM Encomenda
    WHERE id_utilizador = p_id_utilizador
      AND estado_encomenda = 'Carrinho'
    LIMIT 1;

    IF v_encomenda_id IS NULL THEN
        RAISE EXCEPTION 'Não existe carrinho para este utilizador.';
    END IF;

    IF NOT EXISTS (SELECT 1 FROM Encomendas_Produtos WHERE id_encomenda = v_encomenda_id) THEN
        RAISE EXCEPTION 'O carrinho está vazio.';
    END IF;

    UPDATE Encomenda
    SET
        estado_encomenda = 'Pendente',
        data_encomenda   = CURRENT_DATE
    WHERE id_encomenda = v_encomenda_id;
END;
$$;

DROP PROCEDURE IF EXISTS sp_loja_remover_produto(INT, INT);

CREATE OR REPLACE PROCEDURE sp_loja_remover_produto(
    p_id_utilizador INT,
    p_id_produto    INT
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_encomenda_id INT;
BEGIN
    SELECT id_encomenda
    INTO v_encomenda_id
    FROM Encomenda
    WHERE id_utilizador = p_id_utilizador
      AND estado_encomenda = 'Carrinho'
    LIMIT 1;

    IF v_encomenda_id IS NULL THEN
        RAISE EXCEPTION 'Não existe carrinho para este utilizador.';
    END IF;

    DELETE FROM Encomendas_Produtos
    WHERE id_encomenda = v_encomenda_id
      AND id_produto   = p_id_produto;
END;
$$;


-- Admin: CRUD Encomenda (já tinha p_id_exec - mantido)
DROP PROCEDURE IF EXISTS sp_admin_encomenda_criar(INT, DATE, INT, TEXT);

CREATE OR REPLACE PROCEDURE sp_admin_encomenda_criar(
    p_id_exec        INT,
    p_data_encomenda DATE,
    p_id_utilizador  INT,
    p_estado         TEXT
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_tipo_exec TEXT;
BEGIN
    v_tipo_exec := fn_get_tipo_utilizador(p_id_exec);
    IF v_tipo_exec IS NULL OR lower(v_tipo_exec) NOT IN ('admin','gestor') THEN
        RAISE EXCEPTION 'Apenas admin/gestor podem gerir encomendas.';
    END IF;

    IF p_data_encomenda IS NULL THEN
        RAISE EXCEPTION 'Data de encomenda é obrigatória.';
    END IF;

    IF NOT EXISTS (SELECT 1 FROM Utilizador WHERE id_utilizador = p_id_utilizador) THEN
        RAISE EXCEPTION 'Utilizador inválido.';
    END IF;

    INSERT INTO Encomenda(data_encomenda, id_utilizador, estado_encomenda)
    VALUES(p_data_encomenda, p_id_utilizador, COALESCE(NULLIF(btrim(p_estado), ''), 'Pendente'));
END;
$$;


DROP PROCEDURE IF EXISTS sp_admin_encomenda_atualizar(INT, INT, DATE, INT, TEXT);

CREATE OR REPLACE PROCEDURE sp_admin_encomenda_atualizar(
    p_id_exec        INT,
    p_id_encomenda   INT,
    p_data_encomenda DATE,
    p_id_utilizador  INT,
    p_estado         TEXT
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_tipo_exec TEXT;
BEGIN
    v_tipo_exec := fn_get_tipo_utilizador(p_id_exec);
    IF v_tipo_exec IS NULL OR lower(v_tipo_exec) NOT IN ('admin','gestor') THEN
        RAISE EXCEPTION 'Apenas admin/gestor podem gerir encomendas.';
    END IF;

    IF NOT EXISTS (SELECT 1 FROM Encomenda WHERE id_encomenda = p_id_encomenda) THEN
        RAISE EXCEPTION 'Encomenda com id % não existe.', p_id_encomenda;
    END IF;

    IF p_data_encomenda IS NULL THEN
        RAISE EXCEPTION 'Data de encomenda é obrigatória.';
    END IF;

    IF NOT EXISTS (SELECT 1 FROM Utilizador WHERE id_utilizador = p_id_utilizador) THEN
        RAISE EXCEPTION 'Utilizador inválido.';
    END IF;

    UPDATE Encomenda
    SET
        data_encomenda   = p_data_encomenda,
        id_utilizador    = p_id_utilizador,
        estado_encomenda = COALESCE(NULLIF(btrim(p_estado), ''), estado_encomenda)
    WHERE id_encomenda = p_id_encomenda;
END;
$$;


DROP PROCEDURE IF EXISTS sp_admin_encomenda_apagar(INT, INT);

CREATE OR REPLACE PROCEDURE sp_admin_encomenda_apagar(
    p_id_exec      INT,
    p_id_encomenda INT
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_tipo_exec TEXT;
    v_estado    TEXT;
BEGIN
    v_tipo_exec := fn_get_tipo_utilizador(p_id_exec);
    IF v_tipo_exec IS NULL OR lower(v_tipo_exec) NOT IN ('admin','gestor') THEN
        RAISE EXCEPTION 'Apenas admin/gestor podem gerir encomendas.';
    END IF;

    SELECT estado_encomenda
    INTO v_estado
    FROM Encomenda
    WHERE id_encomenda = p_id_encomenda;

    IF v_estado IS NULL THEN
        RAISE EXCEPTION 'Encomenda com id % não existe.', p_id_encomenda;
    END IF;

    IF v_estado <> 'Carrinho' THEN
        UPDATE Produto p
        SET stock = p.stock + ep.quantidade
        FROM Encomendas_Produtos ep
        WHERE ep.id_encomenda = p_id_encomenda
          AND ep.id_produto   = p.id_produto;
    END IF;

    DELETE FROM Encomendas_Produtos WHERE id_encomenda = p_id_encomenda;
    DELETE FROM Encomenda WHERE id_encomenda = p_id_encomenda;
END;
$$;


-- Admin: gerir linhas da encomenda (já tinha p_id_exec - mantido)
DROP PROCEDURE IF EXISTS sp_admin_encomenda_adicionar_item(INT, INT, INT, INT);

CREATE OR REPLACE PROCEDURE sp_admin_encomenda_adicionar_item(
    p_id_exec      INT,
    p_id_encomenda INT,
    p_id_produto   INT,
    p_quantidade   INT
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_tipo_exec TEXT;
BEGIN
    v_tipo_exec := fn_get_tipo_utilizador(p_id_exec);
    IF v_tipo_exec IS NULL OR lower(v_tipo_exec) NOT IN ('admin','gestor') THEN
        RAISE EXCEPTION 'Apenas admin/gestor podem gerir encomendas.';
    END IF;

    IF p_quantidade <= 0 THEN
        RAISE EXCEPTION 'Quantidade inválida.';
    END IF;

    IF NOT EXISTS (SELECT 1 FROM Encomenda WHERE id_encomenda = p_id_encomenda) THEN
        RAISE EXCEPTION 'Encomenda inválida.';
    END IF;

    IF NOT EXISTS (SELECT 1 FROM Produto WHERE id_produto = p_id_produto) THEN
        RAISE EXCEPTION 'Produto inválido.';
    END IF;

    INSERT INTO Encomendas_Produtos(id_encomenda, id_produto, quantidade)
    VALUES(p_id_encomenda, p_id_produto, p_quantidade)
    ON CONFLICT (id_encomenda, id_produto)
    DO UPDATE SET quantidade = Encomendas_Produtos.quantidade + EXCLUDED.quantidade;
END;
$$;


DROP PROCEDURE IF EXISTS sp_admin_encomenda_atualizar_item(INT, INT, INT, INT);

CREATE OR REPLACE PROCEDURE sp_admin_encomenda_atualizar_item(
    p_id_exec      INT,
    p_id_encomenda INT,
    p_id_produto   INT,
    p_quantidade   INT
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_tipo_exec TEXT;
BEGIN
    v_tipo_exec := fn_get_tipo_utilizador(p_id_exec);
    IF v_tipo_exec IS NULL OR lower(v_tipo_exec) NOT IN ('admin','gestor') THEN
        RAISE EXCEPTION 'Apenas admin/gestor podem gerir encomendas.';
    END IF;

    IF p_quantidade <= 0 THEN
        RAISE EXCEPTION 'Quantidade inválida.';
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM Encomendas_Produtos
        WHERE id_encomenda = p_id_encomenda
          AND id_produto   = p_id_produto
    ) THEN
        RAISE EXCEPTION 'Linha de encomenda não existe.';
    END IF;

    UPDATE Encomendas_Produtos
    SET quantidade = p_quantidade
    WHERE id_encomenda = p_id_encomenda
      AND id_produto   = p_id_produto;
END;
$$;


DROP PROCEDURE IF EXISTS sp_admin_encomenda_remover_item(INT, INT, INT);

CREATE OR REPLACE PROCEDURE sp_admin_encomenda_remover_item(
    p_id_exec      INT,
    p_id_encomenda INT,
    p_id_produto   INT
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_tipo_exec TEXT;
BEGIN
    v_tipo_exec := fn_get_tipo_utilizador(p_id_exec);
    IF v_tipo_exec IS NULL OR lower(v_tipo_exec) NOT IN ('admin','gestor') THEN
        RAISE EXCEPTION 'Apenas admin/gestor podem gerir encomendas.';
    END IF;

    DELETE FROM Encomendas_Produtos
    WHERE id_encomenda = p_id_encomenda
      AND id_produto   = p_id_produto;
END;
$$;

-- ALIAS para bater com nomes que tinhas no Django (adicionar_linha / atualizar_linha / remover_linha)
DROP PROCEDURE IF EXISTS sp_admin_encomenda_adicionar_linha(INT, INT, INT, INT);
CREATE OR REPLACE PROCEDURE sp_admin_encomenda_adicionar_linha(p_id_exec INT, p_id_encomenda INT, p_id_produto INT, p_quantidade INT)
LANGUAGE plpgsql
AS $$
BEGIN
    CALL sp_admin_encomenda_adicionar_item(p_id_exec, p_id_encomenda, p_id_produto, p_quantidade);
END;
$$;

DROP PROCEDURE IF EXISTS sp_admin_encomenda_atualizar_linha(INT, INT, INT, INT);
CREATE OR REPLACE PROCEDURE sp_admin_encomenda_atualizar_linha(p_id_exec INT, p_id_encomenda INT, p_id_produto INT, p_quantidade INT)
LANGUAGE plpgsql
AS $$
BEGIN
    CALL sp_admin_encomenda_atualizar_item(p_id_exec, p_id_encomenda, p_id_produto, p_quantidade);
END;
$$;

DROP PROCEDURE IF EXISTS sp_admin_encomenda_remover_linha(INT, INT, INT);
CREATE OR REPLACE PROCEDURE sp_admin_encomenda_remover_linha(p_id_exec INT, p_id_encomenda INT, p_id_produto INT)
LANGUAGE plpgsql
AS $$
BEGIN
    CALL sp_admin_encomenda_remover_item(p_id_exec, p_id_encomenda, p_id_produto);
END;
$$;


-- ============================================================
-- NOTÍCIAS (ADMIN/GESTOR) - JÁ TINHA p_id_exec (mantido)
-- ============================================================

DROP PROCEDURE IF EXISTS sp_admin_noticia_criar(INT, TEXT, TEXT, DATE, INT, INT);

CREATE OR REPLACE PROCEDURE sp_admin_noticia_criar(
    p_id_exec         INT,
    p_titulo          TEXT,
    p_conteudo        TEXT,
    p_data_publicacao DATE,
    p_id_tipo_noticia INT,
    p_autor_id        INT
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_tipo_exec TEXT;
BEGIN
    v_tipo_exec := fn_get_tipo_utilizador(p_id_exec);
    IF v_tipo_exec IS NULL OR lower(v_tipo_exec) NOT IN ('admin','gestor') THEN
        RAISE EXCEPTION 'Apenas admin/gestor podem gerir notícias.';
    END IF;

    IF p_titulo IS NULL OR btrim(p_titulo) = '' THEN
        RAISE EXCEPTION 'O título é obrigatório.';
    END IF;

    IF p_conteudo IS NULL OR btrim(p_conteudo) = '' THEN
        RAISE EXCEPTION 'O conteúdo é obrigatório.';
    END IF;

    IF p_data_publicacao IS NULL THEN
        RAISE EXCEPTION 'A data de publicação é obrigatória.';
    END IF;

    IF p_id_tipo_noticia IS NOT NULL AND NOT EXISTS (
        SELECT 1 FROM Tipo_Noticia WHERE id_tipo_noticia = p_id_tipo_noticia
    ) THEN
        RAISE EXCEPTION 'Tipo de notícia inválido.';
    END IF;

    IF p_autor_id IS NOT NULL AND NOT EXISTS (
        SELECT 1 FROM Utilizador WHERE id_utilizador = p_autor_id
    ) THEN
        RAISE EXCEPTION 'Autor inválido.';
    END IF;

    INSERT INTO Noticia(titulo, conteudo, id_tipo_noticia, autor, data_publicacao)
    VALUES(btrim(p_titulo), btrim(p_conteudo), p_id_tipo_noticia, p_autor_id, p_data_publicacao);
END;
$$;


DROP PROCEDURE IF EXISTS sp_admin_noticia_atualizar(INT, INT, TEXT, TEXT, DATE, INT, INT);

CREATE OR REPLACE PROCEDURE sp_admin_noticia_atualizar(
    p_id_exec         INT,
    p_id_noticia      INT,
    p_titulo          TEXT,
    p_conteudo        TEXT,
    p_data_publicacao DATE,
    p_id_tipo_noticia INT,
    p_autor_id        INT
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_tipo_exec TEXT;
BEGIN
    v_tipo_exec := fn_get_tipo_utilizador(p_id_exec);
    IF v_tipo_exec IS NULL OR lower(v_tipo_exec) NOT IN ('admin','gestor') THEN
        RAISE EXCEPTION 'Apenas admin/gestor podem gerir notícias.';
    END IF;

    IF NOT EXISTS (SELECT 1 FROM Noticia WHERE id_noticia = p_id_noticia) THEN
        RAISE EXCEPTION 'Notícia com id % não existe.', p_id_noticia;
    END IF;

    IF p_titulo IS NULL OR btrim(p_titulo) = '' THEN
        RAISE EXCEPTION 'O título é obrigatório.';
    END IF;

    IF p_conteudo IS NULL OR btrim(p_conteudo) = '' THEN
        RAISE EXCEPTION 'O conteúdo é obrigatório.';
    END IF;

    IF p_data_publicacao IS NULL THEN
        RAISE EXCEPTION 'A data de publicação é obrigatória.';
    END IF;

    IF p_id_tipo_noticia IS NOT NULL AND NOT EXISTS (
        SELECT 1 FROM Tipo_Noticia WHERE id_tipo_noticia = p_id_tipo_noticia
    ) THEN
        RAISE EXCEPTION 'Tipo de notícia inválido.';
    END IF;

    IF p_autor_id IS NOT NULL AND NOT EXISTS (
        SELECT 1 FROM Utilizador WHERE id_utilizador = p_autor_id
    ) THEN
        RAISE EXCEPTION 'Autor inválido.';
    END IF;

    UPDATE Noticia
    SET
        titulo          = btrim(p_titulo),
        conteudo        = btrim(p_conteudo),
        data_publicacao = p_data_publicacao,
        id_tipo_noticia = p_id_tipo_noticia,
        autor           = p_autor_id
    WHERE id_noticia = p_id_noticia;
END;
$$;


DROP PROCEDURE IF EXISTS sp_admin_noticia_apagar(INT, INT);

CREATE OR REPLACE PROCEDURE sp_admin_noticia_apagar(
    p_id_exec    INT,
    p_id_noticia INT
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_tipo_exec TEXT;
BEGIN
    v_tipo_exec := fn_get_tipo_utilizador(p_id_exec);
    IF v_tipo_exec IS NULL OR lower(v_tipo_exec) NOT IN ('admin','gestor') THEN
        RAISE EXCEPTION 'Apenas admin/gestor podem gerir notícias.';
    END IF;

    IF NOT EXISTS (SELECT 1 FROM Noticia WHERE id_noticia = p_id_noticia) THEN
        RAISE EXCEPTION 'Notícia com id % não existe.', p_id_noticia;
    END IF;

    DELETE FROM Noticia
    WHERE id_noticia = p_id_noticia;
END;
$$;

DROP PROCEDURE IF EXISTS sp_cliente_cancelar_encomenda(INT, INT);

CREATE OR REPLACE PROCEDURE sp_cliente_cancelar_encomenda(
    p_id_utilizador INT,
    p_id_encomenda  INT
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_tipo   TEXT;
    v_estado TEXT;
    v_owner  INT;
BEGIN
    -- Só clientes
    v_tipo := fn_get_tipo_utilizador(p_id_utilizador);
    IF v_tipo IS NULL OR lower(v_tipo) <> 'cliente' THEN
        RAISE EXCEPTION 'Apenas clientes podem cancelar encomendas.';
    END IF;

    -- Encomenda existe?
    SELECT id_utilizador, estado_encomenda
    INTO v_owner, v_estado
    FROM Encomenda
    WHERE id_encomenda = p_id_encomenda;

    IF v_owner IS NULL THEN
        RAISE EXCEPTION 'Encomenda não existe.';
    END IF;

    -- Só o dono pode cancelar
    IF v_owner <> p_id_utilizador THEN
        RAISE EXCEPTION 'Não tens permissão para cancelar esta encomenda.';
    END IF;

    -- Regras de cancelamento (ajusta se quiseres)
    IF v_estado = 'Carrinho' THEN
        RAISE EXCEPTION 'Não é possível cancelar um carrinho.';
    END IF;

    IF v_estado = 'Cancelada' THEN
        RAISE EXCEPTION 'A encomenda já está cancelada.';
    END IF;

    -- Só permitir cancelar pendente (recomendado)
    IF v_estado <> 'Pendente' THEN
        RAISE EXCEPTION 'Só podes cancelar encomendas no estado Pendente.';
    END IF;

    -- Cancelar (trigger repõe stock)
    UPDATE Encomenda
    SET estado_encomenda = 'Cancelada'
    WHERE id_encomenda = p_id_encomenda;
END;
$$;


DROP PROCEDURE IF EXISTS sp_loja_diminuir_quantidade(INT, INT, INT);

CREATE OR REPLACE PROCEDURE sp_loja_diminuir_quantidade(
    p_id_utilizador INT,
    p_id_produto    INT,
    p_quantidade    INT
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_tipo_cliente TEXT;
    v_encomenda_id INT;
    v_qtd_atual    INT;
    v_nova_qtd     INT;
BEGIN
    v_tipo_cliente := fn_get_tipo_utilizador(p_id_utilizador);
    IF v_tipo_cliente IS NULL OR lower(v_tipo_cliente) <> 'cliente' THEN
        RAISE EXCEPTION 'Apenas clientes podem alterar o carrinho.';
    END IF;

    IF p_quantidade IS NULL OR p_quantidade <= 0 THEN
        RAISE EXCEPTION 'Quantidade inválida.';
    END IF;

    SELECT id_encomenda
    INTO v_encomenda_id
    FROM Encomenda
    WHERE id_utilizador = p_id_utilizador
      AND estado_encomenda = 'Carrinho'
    LIMIT 1;

    IF v_encomenda_id IS NULL THEN
        RAISE EXCEPTION 'Não existe carrinho para este utilizador.';
    END IF;

    SELECT quantidade
    INTO v_qtd_atual
    FROM Encomendas_Produtos
    WHERE id_encomenda = v_encomenda_id
      AND id_produto   = p_id_produto;

    IF v_qtd_atual IS NULL THEN
        RAISE EXCEPTION 'Produto não existe no carrinho.';
    END IF;

    v_nova_qtd := v_qtd_atual - p_quantidade;

    IF v_nova_qtd <= 0 THEN
        DELETE FROM Encomendas_Produtos
        WHERE id_encomenda = v_encomenda_id
          AND id_produto   = p_id_produto;
    ELSE
        UPDATE Encomendas_Produtos
        SET quantidade = v_nova_qtd
        WHERE id_encomenda = v_encomenda_id
          AND id_produto   = p_id_produto;
    END IF;

    -- Se o carrinho ficar vazio, apagar a encomenda "Carrinho"
    IF NOT EXISTS (SELECT 1 FROM Encomendas_Produtos WHERE id_encomenda = v_encomenda_id) THEN
        DELETE FROM Encomenda
        WHERE id_encomenda = v_encomenda_id
          AND estado_encomenda = 'Carrinho';
    END IF;
END;
$$;

DROP PROCEDURE IF EXISTS sp_utilizador_atualizar_perfil(INT, TEXT, TEXT, TEXT, TEXT);

CREATE OR REPLACE PROCEDURE sp_utilizador_atualizar_perfil(
    p_id_exec INT,
    p_nome    TEXT,
    p_email   TEXT,
    p_morada  TEXT,
    p_nif     TEXT
)
LANGUAGE plpgsql
AS $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM Utilizador WHERE id_utilizador = p_id_exec) THEN
        RAISE EXCEPTION 'Utilizador inválido.';
    END IF;

    IF p_nome IS NULL OR btrim(p_nome) = '' THEN
        RAISE EXCEPTION 'O nome é obrigatório.';
    END IF;

    IF p_email IS NULL OR btrim(p_email) = '' THEN
        RAISE EXCEPTION 'O email é obrigatório.';
    END IF;

    IF p_nif IS NULL OR p_nif !~ '^[0-9]{9}$' THEN
        RAISE EXCEPTION 'O NIF deve ter exatamente 9 dígitos.';
    END IF;

    -- email único (exclui o próprio)
    IF EXISTS (
        SELECT 1 FROM Utilizador
        WHERE lower(email) = lower(p_email)
          AND id_utilizador <> p_id_exec
    ) THEN
        RAISE EXCEPTION 'Já existe outro utilizador com esse email.';
    END IF;

    -- nif único (exclui o próprio)
    IF EXISTS (
        SELECT 1 FROM Utilizador
        WHERE nif = p_nif
          AND id_utilizador <> p_id_exec
    ) THEN
        RAISE EXCEPTION 'Já existe outro utilizador com esse NIF.';
    END IF;

    UPDATE Utilizador
    SET
        nome   = btrim(p_nome),
        email  = btrim(p_email),
        morada = CASE WHEN p_morada IS NULL OR btrim(p_morada) = '' THEN NULL ELSE btrim(p_morada) END,
        nif    = p_nif
    WHERE id_utilizador = p_id_exec;
END;
$$;


DROP PROCEDURE IF EXISTS sp_utilizador_alterar_password(INT, TEXT);

CREATE OR REPLACE PROCEDURE sp_utilizador_alterar_password(
    p_id_exec       INT,
    p_password_hash TEXT
)
LANGUAGE plpgsql
AS $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM Utilizador WHERE id_utilizador = p_id_exec) THEN
        RAISE EXCEPTION 'Utilizador inválido.';
    END IF;

    IF p_password_hash IS NULL OR btrim(p_password_hash) = '' THEN
        RAISE EXCEPTION 'A password é obrigatória.';
    END IF;

    UPDATE Utilizador
    SET password = p_password_hash
    WHERE id_utilizador = p_id_exec;
END;
$$;
