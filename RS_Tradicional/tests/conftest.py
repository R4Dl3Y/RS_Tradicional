import pytest
from django.db import connection

# ---------- TIPOS ----------
@pytest.fixture
def tipo_utilizador_id():
    with connection.cursor() as cur:
        cur.execute(
            "INSERT INTO tipo_utilizador (designacao) VALUES (%s) RETURNING id_tipo_utilizador;",
            ["cliente"]
        )
        return cur.fetchone()[0]

@pytest.fixture
def tipo_produto_id():
    with connection.cursor() as cur:
        cur.execute(
            "INSERT INTO tipo_produto (designacao) VALUES (%s) RETURNING id_tipo_produto;",
            ["gadget"]
        )
        return cur.fetchone()[0]

@pytest.fixture
def estado_carrinho_id():
    with connection.cursor() as cur:
        cur.execute(
            "INSERT INTO estado_carrinho (descricao) VALUES (%s) RETURNING id_estado;",
            ["aberto"]
        )
        return cur.fetchone()[0]

@pytest.fixture
def tipo_noticia_id():
    with connection.cursor() as cur:
        cur.execute(
            "INSERT INTO tipo_noticia (nome) VALUES (%s) RETURNING id_tipo_noticia;",
            ["promo"]
        )
        return cur.fetchone()[0]

# ---------- BASE ----------
@pytest.fixture
def fornecedor_id():
    with connection.cursor() as cur:
        cur.execute("""
            INSERT INTO fornecedor (nome, contacto, email, nif, isSingular, morada, imagem_fornecedor)
            VALUES (%s,%s,%s,%s,%s,%s,%s) RETURNING id_fornecedor;
        """, ["Fornecedor X", "912345678", "fx@example.com", "123456789", True, None, None])
        return cur.fetchone()[0]

@pytest.fixture
def utilizador_id(tipo_utilizador_id):
    with connection.cursor() as cur:
        cur.execute("""
            INSERT INTO utilizador (nome, email, password, morada, nif, imagem_perfil, id_tipo_utilizador)
            VALUES (%s,%s,%s,%s,%s,%s,%s) RETURNING id_utilizador;
        """, ["Alice Teste", "alice@example.com", "hash", "Rua A", "987654321", None, tipo_utilizador_id])
        return cur.fetchone()[0]

@pytest.fixture
def produto_id(tipo_produto_id, fornecedor_id):
    with connection.cursor() as cur:
        cur.execute("""
            INSERT INTO produto (nome, descricao, preco, stock, id_tipo_produto, id_fornecedor)
            VALUES (%s,%s,%s,%s,%s,%s) RETURNING id_produto;
        """, ["Produto A", "desc", 9.99, 10, tipo_produto_id, fornecedor_id])
        return cur.fetchone()[0]

@pytest.fixture
def carrinho_id(utilizador_id, estado_carrinho_id):
    with connection.cursor() as cur:
        cur.execute("""
            INSERT INTO carrinho (id_utilizador, estado)
            VALUES (%s,%s) RETURNING id_carrinho;
        """, [utilizador_id, estado_carrinho_id])
        return cur.fetchone()[0]

@pytest.fixture
def noticia_id(tipo_noticia_id, utilizador_id):
    with connection.cursor() as cur:
        cur.execute("""
            INSERT INTO noticia (titulo, conteudo, id_tipo_noticia, autor, data_publicacao)
            VALUES (%s,%s,%s,%s,%s) RETURNING id_noticia;
        """, ["Promo Dia X", "Conteudo", tipo_noticia_id, utilizador_id, "2025-01-01"])
        return cur.fetchone()[0]
