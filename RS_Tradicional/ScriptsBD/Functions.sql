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
