-- 04_triggers.sql
-- Triggers: stock em encomendas + criação automática de utilizador para fornecedor

-- =========================
-- TRIGGER: stock ao alterar estado da encomenda
-- =========================

DROP TRIGGER IF EXISTS trg_encomenda_stock ON Encomenda;
DROP FUNCTION IF EXISTS fn_trg_encomenda_stock();

CREATE OR REPLACE FUNCTION fn_trg_encomenda_stock()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    v_id_produto INT;
    v_qtd        INT;
    v_stock      INT;
BEGIN
    -- Carrinho -> outro estado: validar e descer stock
    IF (OLD.estado_encomenda = 'Carrinho') AND (NEW.estado_encomenda <> 'Carrinho') THEN

        FOR v_id_produto, v_qtd, v_stock IN
            SELECT ep.id_produto,
                   ep.quantidade,
                   p.stock
            FROM Encomendas_Produtos ep
            JOIN Produto p ON p.id_produto = ep.id_produto
            WHERE ep.id_encomenda = NEW.id_encomenda
        LOOP
            IF v_qtd > v_stock THEN
                RAISE EXCEPTION
                    'Stock insuficiente para o produto % na encomenda % (quantidade=%; stock=%).',
                    v_id_produto, NEW.id_encomenda, v_qtd, v_stock;
            END IF;
        END LOOP;

        UPDATE Produto p
        SET stock = p.stock - ep.quantidade
        FROM Encomendas_Produtos ep
        WHERE ep.id_encomenda = NEW.id_encomenda
          AND ep.id_produto   = p.id_produto;
    END IF;

    -- Repor stock se encomenda passa para "Cancelada" e já não estava cancelada
    IF (OLD.estado_encomenda <> 'Cancelada') AND (NEW.estado_encomenda = 'Cancelada') THEN
        UPDATE Produto p
        SET stock = p.stock + ep.quantidade
        FROM Encomendas_Produtos ep
        WHERE ep.id_encomenda = NEW.id_encomenda
          AND ep.id_produto   = p.id_produto;
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_encomenda_stock
AFTER UPDATE ON Encomenda
FOR EACH ROW
EXECUTE FUNCTION fn_trg_encomenda_stock();


-- =========================
-- TRIGGER: criar Utilizador ao criar Fornecedor
-- =========================

DROP TRIGGER IF EXISTS trg_fornecedor_cria_utilizador ON Fornecedor;
DROP FUNCTION IF EXISTS fn_trg_fornecedor_cria_utilizador();

CREATE OR REPLACE FUNCTION fn_trg_fornecedor_cria_utilizador()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    v_id_tipo_fornecedor INT;
BEGIN
    -- encontrar tipo "fornecedor"
    SELECT id_tipo_utilizador
    INTO v_id_tipo_fornecedor
    FROM Tipo_Utilizador
    WHERE lower(designacao) = 'fornecedor'
    LIMIT 1;

    -- se não existir, não falha; apenas não cria
    IF v_id_tipo_fornecedor IS NULL THEN
        RETURN NEW;
    END IF;

    -- se já existir utilizador com este email, não cria
    IF EXISTS (SELECT 1 FROM Utilizador WHERE lower(email) = lower(NEW.email)) THEN
        RETURN NEW;
    END IF;

    -- criar utilizador "placeholder" (password terá de ser definida pelo admin)
    INSERT INTO Utilizador(
        nome, email, password, morada, nif, id_tipo_utilizador
    )
    VALUES(
        NEW.nome,
        NEW.email,
        'FORNECEDOR_SEM_PASSWORD',
        NEW.morada,
        NEW.nif,
        v_id_tipo_fornecedor
    );

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_fornecedor_cria_utilizador
AFTER INSERT ON Fornecedor
FOR EACH ROW
EXECUTE FUNCTION fn_trg_fornecedor_cria_utilizador();
