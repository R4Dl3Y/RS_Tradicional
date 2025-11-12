DROP TABLE IF EXISTS Imagem_Noticia CASCADE;
DROP TABLE IF EXISTS Produto_Noticia CASCADE;
DROP TABLE IF EXISTS Noticia CASCADE;
DROP TABLE IF EXISTS Tipo_Noticia CASCADE;
DROP TABLE IF EXISTS Produto_Carrinho CASCADE;
DROP TABLE IF EXISTS Carrinho CASCADE;
DROP TABLE IF EXISTS Tipo_Carrinho CASCADE;
DROP TABLE IF EXISTS Imagem_Produto CASCADE;
DROP TABLE IF EXISTS Produto CASCADE;
DROP TABLE IF EXISTS Tipo_Produto CASCADE;
DROP TABLE IF EXISTS Fornecedor CASCADE;
DROP TABLE IF EXISTS Utilizador CASCADE;
DROP TABLE IF EXISTS Tipo_Utilizador CASCADE;

CREATE TABLE Tipo_Utilizador(
    id_tipo_utilizador SERIAL PRIMARY KEY,
    designacao VARCHAR(50) NOT NULL
);

CREATE TABLE Utilizador(
    id_utilizador SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL CHECK (email ~* '^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$'),
    password VARCHAR(255) NOT NULL,
    morada TEXT,
    nif CHAR(9) NOT NULL CHECK (nif ~ '^[0-9]{9}$'),
    imagem_perfil TEXT,
    id_tipo_utilizador INT NULL,
    CONSTRAINT FK_tipo_utilizador FOREIGN KEY (id_tipo_utilizador) REFERENCES Tipo_Utilizador(id_tipo_utilizador) ON DELETE SET NULL
);

CREATE TABLE Fornecedor
(
    id_fornecedor SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    contacto VARCHAR(20) NOT NULL,
    email VARCHAR(255) NOT NULL CHECK (email ~* '^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$'),
    nif CHAR(9) NOT NULL CHECK (nif ~ '^[0-9]{9}$'),
    isSingular BOOL NOT NULL,
    morada TEXT CHECK (isSingular OR morada IS NOT NULL),
    imagem_fornecedor TEXT
);

CREATE TABLE Tipo_Produto
(
    id_tipo_produto SERIAL PRIMARY KEY,
    designacao VARCHAR(100) NOT NULL
);

CREATE TABLE Produto
(
    id_produto SERIAL PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    descricao TEXT,
    preco DECIMAL NOT NULL CHECK (preco >= 0),
    stock INT NOT NULL CHECK (stock >= 0),
    id_tipo_produto INT NULL,
    id_fornecedor INT NULL,
    CONSTRAINT FK_fornecedor FOREIGN KEY (id_fornecedor) REFERENCES Fornecedor(id_fornecedor) ON DELETE SET NULL,
    CONSTRAINT FK_tipo_produto FOREIGN KEY (id_tipo_produto) REFERENCES Tipo_Produto(id_tipo_produto) ON DELETE SET NULL
);

/*Ver alternativas para armazenar as imagens diretamente na bd (binário??)*/
CREATE TABLE Imagem_Produto
(
    id_imagem   SERIAL PRIMARY KEY,
    id_produto  INT NOT NULL,
    caminho     TEXT NOT NULL,
    CONSTRAINT FK_id_produto FOREIGN KEY (id_produto) REFERENCES Produto(id_produto) ON DELETE CASCADE
);

CREATE TABLE Estado_Carrinho
(
    id_estado SERIAL PRIMARY KEY,
    descricao VARCHAR(50) NOT NULL
);

CREATE TABLE Carrinho
(
    id_carrinho SERIAL PRIMARY KEY,
    id_utilizador INT NOT NULL,
    estado INT NULL,
    CONSTRAINT FK_id_utilizador FOREIGN KEY (id_utilizador) REFERENCES Utilizador(id_utilizador) ON DELETE CASCADE,
    CONSTRAINT FK_estado FOREIGN KEY (estado) REFERENCES Estado_Carrinho(id_estado) ON DELETE SET NULL
);

CREATE TABLE Produto_Carrinho
(
    id_carrinho  INT NOT NULL REFERENCES Carrinho(id_carrinho) ON DELETE CASCADE,
    id_produto  INT NOT NULL REFERENCES Produto(id_produto) ON DELETE CASCADE,
    quantidade INT DEFAULT 1,
    PRIMARY KEY (id_carrinho, id_produto)
);

CREATE TABLE Tipo_Noticia
(
    id_tipo_noticia SERIAL PRIMARY KEY,
    nome VARCHAR(50)
);

CREATE TABLE Noticia
(
    id_noticia SERIAL PRIMARY KEY,
    titulo VARCHAR(200) NOT NULL,
    conteudo VARCHAR(255) NOT NULL,
    id_tipo_noticia INT NULL,
    autor INT NULL,
    data_publicacao DATE NOT NULL,
    CONSTRAINT FK_id_tipo_noticia FOREIGN KEY (id_tipo_noticia) REFERENCES Tipo_Noticia(id_tipo_noticia) ON DELETE SET NULL,
    CONSTRAINT FK_autor FOREIGN KEY (autor) REFERENCES Utilizador(id_utilizador) ON DELETE SET NULL
);

/*IMAGENS (1:N com notícia)*/
CREATE TABLE Imagem_Noticia 
(
    id_imagem     SERIAL PRIMARY KEY,
    id_noticia    INT NULL,
    uri           TEXT NOT NULL, 
    CONSTRAINT FK_id_noticia FOREIGN KEY (id_noticia) REFERENCES Noticia(id_noticia) ON DELETE SET NULL
);

CREATE TABLE Produto_Noticia
(
    id_noticia  INT NOT NULL REFERENCES Noticia(id_noticia) ON DELETE CASCADE,
    id_produto  INT NOT NULL REFERENCES Produto(id_produto) ON DELETE CASCADE,
    PRIMARY KEY (id_noticia, id_produto)
);


/*
    vão ser criadas em MONGO

CREATE TABLE IF NOT EXISTS public."Encomenda"
(
    id_encomenda integer NOT NULL,
    data date NOT NULL,
    id_utilizador integer NOT NULL,
    id_estado integer NOT NULL,
    CONSTRAINT "Encomenda_pkey" PRIMARY KEY (id_encomenda)
);

CREATE TABLE IF NOT EXISTS public."Encomendas_Produtos"
(
    id_encomenda integer NOT NULL,
    id_produto integer NOT NULL,
    quantidade integer,
    CONSTRAINT id_encomenda PRIMARY KEY (id_encomenda, id_produto)
);

Faturação também
*/
