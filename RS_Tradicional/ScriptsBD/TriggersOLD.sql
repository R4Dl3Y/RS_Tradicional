DROP FUNCTION IF EXISTS trg_normaliza_email_utilizador() CASCADE;
DROP TRIGGER IF EXISTS normaliza_email_utilizador ON Utilizador;

CREATE OR REPLACE FUNCTION trg_normaliza_email_utilizador()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    -- Garante que o email fica sempre em minúsculas
    IF NEW.email IS NOT NULL THEN
        NEW.email := lower(NEW.email);
    END IF;
    RETURN NEW;
END;
$$;

CREATE TRIGGER normaliza_email_utilizador
BEFORE INSERT OR UPDATE ON Utilizador
FOR EACH ROW
EXECUTE FUNCTION trg_normaliza_email_utilizador();


DROP FUNCTION IF EXISTS trg_normaliza_email_fornecedor() CASCADE;
DROP TRIGGER IF EXISTS normaliza_email_fornecedor ON Fornecedor;

CREATE OR REPLACE FUNCTION trg_normaliza_email_fornecedor()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    IF NEW.email IS NOT NULL THEN
        NEW.email := lower(NEW.email);
    END IF;
    RETURN NEW;
END;
$$;

CREATE TRIGGER normaliza_email_fornecedor
BEFORE INSERT OR UPDATE ON Fornecedor
FOR EACH ROW
EXECUTE FUNCTION trg_normaliza_email_fornecedor();


DROP FUNCTION IF EXISTS trg_verifica_quantidade_stock_carrinho() CASCADE;
DROP TRIGGER IF EXISTS verifica_quantidade_stock_carrinho ON Produto_Carrinho;

CREATE OR REPLACE FUNCTION trg_verifica_quantidade_stock_carrinho()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    v_stock_atual INT;
BEGIN
    -- quantidade tem de ser positiva
    IF NEW.quantidade IS NULL OR NEW.quantidade <= 0 THEN
        RAISE EXCEPTION 'Quantidade tem de ser > 0';
    END IF;

    -- obtém stock do produto
    SELECT stock INTO v_stock_atual
    FROM Produto
    WHERE id_produto = NEW.id_produto;

    IF v_stock_atual IS NULL THEN
        RAISE EXCEPTION 'Produto % não existe', NEW.id_produto;
    END IF;

    -- se for INSERT, comparamos NEW.quantidade com stock
    -- se for UPDATE, comparamos diferença (NEW - OLD)
    IF TG_OP = 'INSERT' THEN
        IF NEW.quantidade > v_stock_atual THEN
            RAISE EXCEPTION 'Stock insuficiente para o produto %, stock: %, pedido: %',
                NEW.id_produto, v_stock_atual, NEW.quantidade;
        END IF;
    ELSIF TG_OP = 'UPDATE' THEN
        IF NEW.quantidade > OLD.quantidade THEN
            IF (NEW.quantidade - OLD.quantidade) > v_stock_atual THEN
                RAISE EXCEPTION 'Stock insuficiente para atualizar o produto %, stock: %, pedido extra: %',
                    NEW.id_produto, v_stock_atual, (NEW.quantidade - OLD.quantidade);
            END IF;
        END IF;
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER verifica_quantidade_stock_carrinho
BEFORE INSERT OR UPDATE ON Produto_Carrinho
FOR EACH ROW
EXECUTE FUNCTION trg_verifica_quantidade_stock_carrinho();



DROP FUNCTION IF EXISTS trg_atualiza_stock_produto_carrinho() CASCADE;
DROP TRIGGER IF EXISTS atualiza_stock_produto_carrinho ON Produto_Carrinho;

CREATE OR REPLACE FUNCTION trg_atualiza_stock_produto_carrinho()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    -- INSERT: diminui o stock
    IF TG_OP = 'INSERT' THEN
        UPDATE Produto
        SET stock = stock - NEW.quantidade
        WHERE id_produto = NEW.id_produto;

    -- UPDATE: ajusta pela diferença
    ELSIF TG_OP = 'UPDATE' THEN
        UPDATE Produto
        SET stock = stock - (NEW.quantidade - OLD.quantidade)
        WHERE id_produto = NEW.id_produto;

    -- DELETE: devolve stock
    ELSIF TG_OP = 'DELETE' THEN
        UPDATE Produto
        SET stock = stock + OLD.quantidade
        WHERE id_produto = OLD.id_produto;
    END IF;

    RETURN NULL; -- AFTER trigger em statement row-based para UPDATEs
END;
$$;

CREATE TRIGGER atualiza_stock_produto_carrinho
AFTER INSERT OR UPDATE OR DELETE ON Produto_Carrinho
FOR EACH ROW
EXECUTE FUNCTION trg_atualiza_stock_produto_carrinho();



DROP FUNCTION IF EXISTS trg_definir_data_publicacao() CASCADE;
DROP TRIGGER IF EXISTS definir_data_publicacao ON Noticia;

CREATE OR REPLACE FUNCTION trg_definir_data_publicacao()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    -- Se a data não for indicada, usa a data atual
    IF NEW.data_publicacao IS NULL THEN
        NEW.data_publicacao := CURRENT_DATE;
    END IF;
    RETURN NEW;
END;
$$;

CREATE TRIGGER definir_data_publicacao
BEFORE INSERT ON Noticia
FOR EACH ROW
EXECUTE FUNCTION trg_definir_data_publicacao();


------------------------------------------------------------------------------------------

-- Trigger – NIF único em Utilizador

-- Impede NIF duplicado em Utilizador
DROP FUNCTION IF EXISTS trg_verifica_nif_utilizador() CASCADE;
DROP TRIGGER IF EXISTS verifica_nif_utilizador ON Utilizador;

CREATE OR REPLACE FUNCTION trg_verifica_nif_utilizador()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    v_exists INT;
BEGIN
    IF NEW.nif IS NOT NULL THEN
        SELECT COUNT(*) INTO v_exists
        FROM Utilizador
        WHERE nif = NEW.nif
          AND id_utilizador <> COALESCE(NEW.id_utilizador, -1);

        IF v_exists > 0 THEN
            RAISE EXCEPTION 'Já existe um utilizador com o NIF %', NEW.nif;
        END IF;
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER verifica_nif_utilizador
BEFORE INSERT OR UPDATE ON Utilizador
FOR EACH ROW
EXECUTE FUNCTION trg_verifica_nif_utilizador();


--Trigger – Validar preço e stock em Produto
-- Garante preço e stock válidos no Produto
DROP FUNCTION IF EXISTS trg_valida_produto() CASCADE;
DROP TRIGGER IF EXISTS valida_produto ON Produto;

CREATE OR REPLACE FUNCTION trg_valida_produto()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    IF NEW.preco IS NULL OR NEW.preco < 0 THEN
        RAISE EXCEPTION 'Preço do produto % inválido (não pode ser negativo ou nulo)', NEW.nome;
    END IF;

    IF NEW.stock IS NULL OR NEW.stock < 0 THEN
        RAISE EXCEPTION 'Stock do produto % inválido (não pode ser negativo ou nulo)', NEW.nome;
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER valida_produto
BEFORE INSERT OR UPDATE ON Produto
FOR EACH ROW
EXECUTE FUNCTION trg_valida_produto();


-- Trigger - Impede finalizar carrinho sem linhas de produtos
DROP FUNCTION IF EXISTS trg_valida_carrinho_finalizado() CASCADE;
DROP TRIGGER IF EXISTS valida_carrinho_finalizado ON Carrinho;

CREATE OR REPLACE FUNCTION trg_valida_carrinho_finalizado()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    v_desc_estado   TEXT;
    v_qtd_linhas    INT;
BEGIN
    -- Obtem a descrição do estado novo
    SELECT descricao INTO v_desc_estado
    FROM Estado_Carrinho
    WHERE id_estado = NEW.estado;

    -- Só valida se o estado for 'Finalizado'
    IF v_desc_estado = 'Finalizado' THEN
        SELECT COUNT(*) INTO v_qtd_linhas
        FROM Produto_Carrinho
        WHERE id_carrinho = NEW.id_carrinho;

        IF v_qtd_linhas = 0 THEN
            RAISE EXCEPTION 'Não é possível finalizar um carrinho sem produtos (id_carrinho=%).',
                NEW.id_carrinho;
        END IF;
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER valida_carrinho_finalizado
BEFORE UPDATE ON Carrinho
FOR EACH ROW
EXECUTE FUNCTION trg_valida_carrinho_finalizado();

