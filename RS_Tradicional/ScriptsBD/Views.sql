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
