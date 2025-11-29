DROP FUNCTION IF EXISTS export_utilizadores() CASCADE;

CREATE OR REPLACE FUNCTION export_utilizadores()
RETURNS TABLE (
    id_utilizador      INT,
    nome               VARCHAR,
    email              VARCHAR,
    nif                CHAR(9),
    morada             TEXT,
    tipo_utilizador    VARCHAR
)
LANGUAGE sql
AS $$
    SELECT u.id_utilizador,
           u.nome,
           u.email,
           u.nif,
           u.morada,
           tu.designacao AS tipo_utilizador
    FROM Utilizador u
    LEFT JOIN Tipo_Utilizador tu
           ON u.id_tipo_utilizador = tu.id_tipo_utilizador
    ORDER BY u.id_utilizador;
$$;

DROP FUNCTION IF EXISTS export_produtos() CASCADE;

CREATE OR REPLACE FUNCTION export_produtos()
RETURNS TABLE (
    id_produto      INT,
    nome_produto    VARCHAR,
    descricao       TEXT,
    preco           DECIMAL,
    stock           INT,
    tipo_produto    VARCHAR,
    fornecedor      VARCHAR,
    nif_fornecedor  CHAR(9)
)
LANGUAGE sql
AS $$
    SELECT p.id_produto,
           p.nome AS nome_produto,
           p.descricao,
           p.preco,
           p.stock,
           tp.designacao AS tipo_produto,
           f.nome        AS fornecedor,
           f.nif         AS nif_fornecedor
    FROM Produto p
    LEFT JOIN Tipo_Produto tp
           ON p.id_tipo_produto = tp.id_tipo_produto
    LEFT JOIN Fornecedor f
           ON p.id_fornecedor = f.id_fornecedor
    ORDER BY p.id_produto;
$$;


DROP FUNCTION IF EXISTS export_carrinhos_resumo() CASCADE;

CREATE OR REPLACE FUNCTION export_carrinhos_resumo()
RETURNS TABLE (
    id_carrinho   INT,
    utilizador    VARCHAR,
    estado        VARCHAR,
    total_linhas  INT,
    total_valor   DECIMAL
)
LANGUAGE sql
AS $$
    SELECT c.id_carrinho,
           u.nome AS utilizador,
           ec.descricao AS estado,
           COALESCE(SUM(pc.quantidade), 0) AS total_linhas,
           COALESCE(SUM(pc.quantidade * p.preco), 0)::DECIMAL AS total_valor
    FROM Carrinho c
    JOIN Utilizador u
      ON c.id_utilizador = u.id_utilizador
    LEFT JOIN Estado_Carrinho ec
      ON c.estado = ec.id_estado
    LEFT JOIN Produto_Carrinho pc
      ON c.id_carrinho = pc.id_carrinho
    LEFT JOIN Produto p
      ON pc.id_produto = p.id_produto
    GROUP BY c.id_carrinho, u.nome, ec.descricao
    ORDER BY c.id_carrinho;
$$;



DROP FUNCTION IF EXISTS export_carrinho_detalhe(INT) CASCADE;

CREATE OR REPLACE FUNCTION export_carrinho_detalhe(p_id_carrinho INT)
RETURNS TABLE (
    id_carrinho      INT,
    utilizador       VARCHAR,
    estado           VARCHAR,
    id_produto       INT,
    nome_produto     VARCHAR,
    quantidade       INT,
    preco_unitario   DECIMAL,
    subtotal         DECIMAL
)
LANGUAGE sql
AS $$
    SELECT c.id_carrinho,
           u.nome AS utilizador,
           ec.descricao AS estado,
           p.id_produto,
           p.nome AS nome_produto,
           pc.quantidade,
           p.preco AS preco_unitario,
           (pc.quantidade * p.preco)::DECIMAL AS subtotal
    FROM Carrinho c
    JOIN Utilizador u
      ON c.id_utilizador = u.id_utilizador
    LEFT JOIN Estado_Carrinho ec
      ON c.estado = ec.id_estado
    JOIN Produto_Carrinho pc
      ON c.id_carrinho = pc.id_carrinho
    JOIN Produto p
      ON pc.id_produto = p.id_produto
    WHERE c.id_carrinho = p_id_carrinho
    ORDER BY p.id_produto;
$$;


DROP FUNCTION IF EXISTS export_noticias() CASCADE;

CREATE OR REPLACE FUNCTION export_noticias()
RETURNS TABLE (
    id_noticia        INT,
    titulo            VARCHAR,
    conteudo          VARCHAR,
    tipo_noticia      VARCHAR,
    autor             VARCHAR,
    data_publicacao   DATE
)
LANGUAGE sql
AS $$
    SELECT n.id_noticia,
           n.titulo,
           n.conteudo,
           tn.nome AS tipo_noticia,
           u.nome  AS autor,
           n.data_publicacao
    FROM Noticia n
    LEFT JOIN Tipo_Noticia tn
           ON n.id_tipo_noticia = tn.id_tipo_noticia
    LEFT JOIN Utilizador u
           ON n.autor = u.id_utilizador
    ORDER BY n.data_publicacao DESC, n.id_noticia;
$$;

------------------------------------------------------------------------------------------

-- Exportar encomendas (resumo)
-- Lista todas as encomendas com cliente, estado e total.

DROP FUNCTION IF EXISTS export_encomendas_resumo() CASCADE;

CREATE OR REPLACE FUNCTION export_encomendas_resumo()
RETURNS TABLE (
    id_encomenda   INT,
    data_encomenda DATE,
    cliente        VARCHAR,
    estado         VARCHAR,
    total_encomenda DECIMAL
)
LANGUAGE sql
AS $$
    SELECT e.id_encomenda,
           e.data_encomenda,
           u.nome AS cliente,
           ec.descricao AS estado,
           e.valor_total::DECIMAL AS total_encomenda
    FROM Encomenda e
    JOIN Utilizador u
      ON e.id_utilizador = u.id_utilizador
    JOIN Estado_Carrinho ec
      ON e.estado = ec.id_estado
    ORDER BY e.data_encomenda DESC, e.id_encomenda;
$$;


-- Exportar detalhe de uma encomenda
-- Semelhante ao carrinho_detalhe, mas já depois da encomenda finalizada.

DROP FUNCTION IF EXISTS export_encomenda_detalhe(INT) CASCADE;

CREATE OR REPLACE FUNCTION export_encomenda_detalhe(p_id_encomenda INT)
RETURNS TABLE (
    id_encomenda    INT,
    data_encomenda  DATE,
    cliente         VARCHAR,
    estado          VARCHAR,
    id_produto      INT,
    nome_produto    VARCHAR,
    quantidade      INT,
    preco_unitario  DECIMAL,
    subtotal        DECIMAL
)
LANGUAGE sql
AS $$
    SELECT e.id_encomenda,
           e.data_encomenda,
           u.nome AS cliente,
           ec.descricao AS estado,
           p.id_produto,
           p.nome AS nome_produto,
           le.quantidade,
           le.preco_unitario,
           (le.quantidade * le.preco_unitario)::DECIMAL AS subtotal
    FROM Encomenda e
    JOIN Utilizador u
      ON e.id_utilizador = u.id_utilizador
    JOIN Estado_Carrinho ec
      ON e.estado = ec.id_estado
    JOIN Linha_Encomenda le
      ON e.id_encomenda = le.id_encomenda
    JOIN Produto p
      ON le.id_produto = p.id_produto
    WHERE e.id_encomenda = p_id_encomenda
    ORDER BY p.id_produto;
$$;

-- Exportar imagens associadas (produtos e notícias)
-- Útil para auditoria ou migração de ficheiros.

DROP FUNCTION IF EXISTS export_imagens() CASCADE;

CREATE OR REPLACE FUNCTION export_imagens()
RETURNS TABLE (
    origem        VARCHAR,   -- 'Produto' ou 'Noticia'
    id_origem     INT,
    nome_origem   VARCHAR,
    id_imagem     INT,
    caminho       TEXT
)
LANGUAGE sql
AS $$
    -- Imagens de produto
    SELECT 'Produto'::VARCHAR AS origem,
           p.id_produto      AS id_origem,
           p.nome            AS nome_origem,
           ip.id_imagem,
           ip.caminho        AS caminho
    FROM Produto p
    JOIN Imagem_Produto ip
      ON p.id_produto = ip.id_produto

    UNION ALL

    -- Imagens de notícia
    SELECT 'Noticia'::VARCHAR AS origem,
           n.id_noticia       AS id_origem,
           n.titulo           AS nome_origem,
           inot.id_imagem,
           inot.caminho       AS caminho
    FROM Noticia n
    JOIN Imagem_Noticia inot
      ON n.id_noticia = inot.id_noticia

    ORDER BY origem, id_origem, id_imagem;
$$;
