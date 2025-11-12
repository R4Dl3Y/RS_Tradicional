import pytest, django
from django.db import connection
django.setup()

# --------- Tipo_Produto ----------
@pytest.mark.django_db(transaction=True)
def test_sp_tipo_produto_create():
    with connection.cursor() as cur:
        cur.execute("BEGIN;")
        try:
            cur.execute("CALL sp_tipo_produto_create(%s, %s);", ["acessorio", None])
            new_id = cur.fetchone()[0]
            cur.execute("SELECT designacao FROM tipo_produto WHERE id_tipo_produto=%s;", [new_id])
            assert cur.fetchone()[0] == "acessorio"
        finally:
            cur.execute("ROLLBACK;")

@pytest.mark.django_db(transaction=True)
def test_sp_tipo_produto_get(tipo_produto_id):
    with connection.cursor() as cur:
        cur.execute("BEGIN;")
        try:
            cur.execute("CALL sp_tipo_produto_get(%s, %s);", [tipo_produto_id, "curtp"])
            cur.execute("FETCH ALL FROM curtp;")
            rows = cur.fetchall()
            assert len(rows) == 1 and rows[0][0] == tipo_produto_id
        finally:
            cur.execute("ROLLBACK;")

@pytest.mark.django_db(transaction=True)
def test_sp_tipo_produto_update(tipo_produto_id):
    with connection.cursor() as cur:
        cur.execute("BEGIN;")
        try:
            cur.execute("CALL sp_tipo_produto_update(%s, %s);", [tipo_produto_id, "categoria"])
            cur.execute("SELECT designacao FROM tipo_produto WHERE id_tipo_produto=%s;", [tipo_produto_id])
            assert cur.fetchone()[0] == "categoria"
        finally:
            cur.execute("ROLLBACK;")

@pytest.mark.django_db(transaction=True)
def test_sp_tipo_produto_delete(tipo_produto_id):
    with connection.cursor() as cur:
        cur.execute("BEGIN;")
        try:
            cur.execute("CALL sp_tipo_produto_delete(%s);", [tipo_produto_id])
            cur.execute("SELECT COUNT(*) FROM tipo_produto WHERE id_tipo_produto=%s;", [tipo_produto_id])
            assert cur.fetchone()[0] == 0
        finally:
            cur.execute("ROLLBACK;")

# --------- Produto ----------
@pytest.mark.django_db(transaction=True)
def test_sp_produto_create(tipo_produto_id, fornecedor_id):
    with connection.cursor() as cur:
        cur.execute("BEGIN;")
        try:
            args = ["P Novo", "desc", 5.5, 3, tipo_produto_id, fornecedor_id, None]
            cur.execute("CALL sp_produto_create(%s,%s,%s,%s,%s,%s, %s);", args)
            new_id = cur.fetchone()[0]
            cur.execute("SELECT nome, stock FROM produto WHERE id_produto=%s;", [new_id])
            nome, stock = cur.fetchone()
            assert nome == "P Novo" and stock == 3
        finally:
            cur.execute("ROLLBACK;")

@pytest.mark.django_db(transaction=True)
def test_sp_produto_get(produto_id):
    with connection.cursor() as cur:
        cur.execute("BEGIN;")
        try:
            cur.execute("CALL sp_produto_get(%s, %s);", [produto_id, "curp"])
            cur.execute("FETCH ALL FROM curp;")
            rows = cur.fetchall()
            assert len(rows) == 1 and rows[0][0] == produto_id
        finally:
            cur.execute("ROLLBACK;")

@pytest.mark.django_db(transaction=True)
def test_sp_produto_update(produto_id):
    with connection.cursor() as cur:
        cur.execute("BEGIN;")
        try:
            cur.execute("CALL sp_produto_update(%s,%s,%s,%s,%s,%s,%s);",
                        [produto_id, "Nome Z", None, 7.75, 99, None, None])
            cur.execute("SELECT nome, preco, stock FROM produto WHERE id_produto=%s;", [produto_id])
            nome, preco, stock = cur.fetchone()
            assert nome == "Nome Z" and float(preco) == 7.75 and stock == 99
        finally:
            cur.execute("ROLLBACK;")

@pytest.mark.django_db(transaction=True)
def test_sp_produto_delete(produto_id):
    with connection.cursor() as cur:
        cur.execute("BEGIN;")
        try:
            cur.execute("CALL sp_produto_delete(%s);", [produto_id])
            cur.execute("SELECT COUNT(*) FROM produto WHERE id_produto=%s;", [produto_id])
            assert cur.fetchone()[0] == 0
        finally:
            cur.execute("ROLLBACK;")
