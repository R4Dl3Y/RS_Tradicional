-- 01_roles.sql
-- =========================================
-- ROLES e permissões base
-- =========================================

-- Primeiro remover roles de login, depois lógicas e base
DROP ROLE IF EXISTS rs_admin_user;
DROP ROLE IF EXISTS rs_gestor_user;
DROP ROLE IF EXISTS rs_fornecedor_user;
DROP ROLE IF EXISTS rs_cliente_user;

DROP ROLE IF EXISTS rs_admin;
DROP ROLE IF EXISTS rs_gestor;
DROP ROLE IF EXISTS rs_fornecedor;
DROP ROLE IF EXISTS rs_cliente;
DROP ROLE IF EXISTS rs_base;

-- -----------------------------------------
-- Role base (sem login)
-- -----------------------------------------
CREATE ROLE rs_base NOLOGIN;

-- Perfis "lógicos" (sem login, herdam da base)
CREATE ROLE rs_cliente    NOLOGIN INHERIT IN ROLE rs_base;
CREATE ROLE rs_fornecedor NOLOGIN INHERIT IN ROLE rs_base;
CREATE ROLE rs_gestor     NOLOGIN INHERIT IN ROLE rs_base;
CREATE ROLE rs_admin      NOLOGIN INHERIT IN ROLE rs_base;

-- -----------------------------------------
-- Roles de login (EXEMPLO – muda as passwords!)
-- Podes usar estes users só para demonstração no pgAdmin
-- Não precisam de ser os users do settings.py do Django.
-- -----------------------------------------
CREATE ROLE rs_admin_user LOGIN PASSWORD 'MudaEstaPasswordAdmin';
GRANT rs_admin TO rs_admin_user;

CREATE ROLE rs_gestor_user LOGIN PASSWORD 'MudaEstaPasswordGestor';
GRANT rs_gestor TO rs_gestor_user;

CREATE ROLE rs_fornecedor_user LOGIN PASSWORD 'MudaEstaPasswordFornecedor';
GRANT rs_fornecedor TO rs_fornecedor_user;

CREATE ROLE rs_cliente_user LOGIN PASSWORD 'MudaEstaPasswordCliente';
GRANT rs_cliente TO rs_cliente_user;

-- -----------------------------------------
-- Permissões de schema
-- -----------------------------------------
GRANT USAGE ON SCHEMA public TO rs_admin, rs_gestor, rs_fornecedor, rs_cliente;

-- =========================================
-- Permissões em TABELAS e VIEWS
-- (all tables in schema public inclui views também)
-- =========================================

-- Admin: full access
GRANT SELECT, INSERT, UPDATE, DELETE ON
    tipo_utilizador,
    utilizador,
    fornecedor,
    tipo_produto,
    produto,
    imagem_produto,
    tipo_noticia,
    noticia,
    imagem_noticia,
    produto_noticia,
    encomenda,
    encomendas_produtos
TO rs_admin;

-- Gestor: quase tudo (sem deletes em utilizador/tipo_utilizador se quiseres ser mais rígido)
GRANT SELECT, INSERT, UPDATE ON
    tipo_utilizador,
    utilizador,
    fornecedor,
    tipo_produto,
    produto,
    tipo_noticia,
    noticia,
    encomenda,
    encomendas_produtos
TO rs_gestor;

-- Fornecedor: leitura de tipos e produtos (opera via procedures)
GRANT SELECT ON
    tipo_produto,
    produto,
    fornecedor
TO rs_fornecedor;

-- Cliente: leitura de produtos/notícias (opera via procedures)
GRANT SELECT ON
    tipo_produto,
    produto,
    tipo_noticia,
    noticia
TO rs_cliente;

-- Se quiseres simplificar e garantir que também apanhas as views:
-- (opcional, se já tiveres as GRANTs específicos em cima)
GRANT SELECT ON ALL TABLES IN SCHEMA public TO rs_admin;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO rs_gestor;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO rs_fornecedor;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO rs_cliente;

-- =========================================
-- Permitir execução de FUNCTIONS/PROCEDURES
-- =========================================

GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO rs_admin;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO rs_gestor;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO rs_fornecedor;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO rs_cliente;
