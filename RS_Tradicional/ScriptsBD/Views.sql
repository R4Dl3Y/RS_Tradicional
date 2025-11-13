--Views Simples Utilizadores

CREATE VIEW vw_listarUtilizadores AS

SELECT id_utilizador, nome, email, morada, nif, tp.designacao FROM utilizador
JOIN tipo_utilizador AS tp
ON utilizador.id_tipo_utilizador = tp.id_tipo_utilizador;


--Views Simples Produtos

CREATE VIEW vw_listarProdutos AS

SELECT id_produto, produto.nome, descricao, preco, stock, tp.designacao AS TipoProduto, fn.nome AS Fornecedor FROM produto
JOIN tipo_produto AS tp
ON produto.id_tipo_produto = tp.id_tipo_produto
JOIN fornecedor AS fn
ON produto.id_fornecedor = fn.id_fornecedor;


--Views Materializadas Utilizadores

CREATE MATERIALIZED VIEW mvw_utilizadoresMoradaViseu AS
SELECT id_utilizador, nome, email, morada, nif, tp.designacao FROM utilizador
JOIN tipo_utilizador AS tp
ON utilizador.id_tipo_utilizador = tp.id_tipo_utilizador
WHERE morada LIKE '%Viseu%' OR morada LIKE '%viseu%';

--Views Materializadas Produtos

CREATE MATERIALIZED VIEW mvw_produtosComMuitoStock AS
SELECT id_produto, produto.nome, descricao, stock, tp.designacao AS TipoProduto, fn.nome AS Fornecedor FROM produto
JOIN tipo_produto AS tp
ON produto.id_tipo_produto = tp.id_tipo_produto
JOIN fornecedor AS fn
ON produto.id_fornecedor = fn.id_fornecedor
ORDER BY stock DESC 
LIMIT 10;

----------------

-- View simples: Últimas encomendas
CREATE OR REPLACE VIEW vw_ultimas_encomendas AS
SELECT e.id_encomenda,
       e.data_encomenda,
       e.valor_total,
       ec.descricao AS estado
  FROM encomenda e
  JOIN estado_carrinho ec ON e.estado = ec.id_estado
ORDER BY e.data_encomenda DESC
LIMIT 20;

-- View simples: Notícias por tipo
CREATE OR REPLACE VIEW vw_noticias_por_tipo AS
SELECT n.id_noticia,
       n.titulo,
       tn.nome AS tipo_noticia,
       n.data_publicacao
  FROM noticia n
  JOIN tipo_noticia tn ON n.id_tipo_noticia = tn.id_tipo_noticia
ORDER BY n.data_publicacao DESC;


-- View materializada: Quantidade de imagens por notícia
CREATE MATERIALIZED VIEW vw_qtd_imagens_por_noticia AS
SELECT n.id_noticia,
       n.titulo,
       COUNT(i.id_imagem) AS total_imagens
  FROM noticia n
  LEFT JOIN imagem_noticia i ON n.id_noticia = i.id_noticia
GROUP BY n.id_noticia, n.titulo
ORDER BY total_imagens DESC;

-- View materializada: Resumo de encomendas por estado
CREATE MATERIALIZED VIEW vw_encomendas_por_estado AS
SELECT
  ec.descricao AS estado,
  COUNT(e.id_encomenda) AS qtd_encomendas,
  COALESCE(SUM(e.valor_total), 0) AS total_faturado
FROM encomenda e
JOIN estado_carrinho ec ON e.estado = ec.id_estado
GROUP BY ec.descricao
ORDER BY qtd_encomendas DESC;
