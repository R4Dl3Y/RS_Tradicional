import pytest, django
from django.db import connection
django.setup()

@pytest.mark.django_db(transaction=True)
def test_sp_produto_carrinho_create(carrinho_id, produto_id):
    with connection.cursor() as cur:
        cur.execute("BEGIN;")
        try:
            cur.execute("CALL sp_produto_carrinho_create(%s,%s,%s);", [carrinho_id, produto_id, 2])
            cur.execute("SELECT quantidade FROM produto_carrinho WHERE id_carrinho=%s AND id_produto=%s;", [carrinho_id, produto_id])
            assert cur.fetchone()[0] == 2
        finally:
            cur.execute("ROLLBACK;")

@pytest.mark.django_db(transaction=True)
def test_sp_produto_carrinho_get(carrinho_id, produto_id):
    with connection.cursor() as cur:
        cur.execute("BEGIN;")
        try:
            cur.execute("INSERT INTO produto_carrinho (id_carrinho, id_produto, quantidade) VALUES (%s,%s,%s);",
                        [carrinho_id, produto_id, 1])
            cur.execute("CALL sp_produto_carrinho_get(%s,%s,%s);", [carrinho_id, produto_id, "curpc"])
            cur.execute("FETCH ALL FROM curpc;")
            rows = cur.fetchall()
            assert len(rows) == 1 and rows[0][0] == carrinho_id and rows[0][1] == produto_id
        finally:
            cur.execute("ROLLBACK;")

@pytest.mark.django_db(transaction=True)
def test_sp_produto_carrinho_update(carrinho_id, produto_id):
    with connection.cursor() as cur:
        cur.execute("BEGIN;")
        try:
            cur.execute("INSERT INTO produto_carrinho (id_carrinho, id_produto, quantidade) VALUES (%s,%s,%s);",
                        [carrinho_id, produto_id, 1])
            cur.execute("CALL sp_produto_carrinho_update(%s,%s,%s);", [carrinho_id, produto_id, 5])
            cur.execute("SELECT quantidade FROM produto_carrinho WHERE id_carrinho=%s AND id_produto=%s;", [carrinho_id, produto_id])
            assert cur.fetchone()[0] == 5
        finally:
            cur.execute("ROLLBACK;")

@pytest.mark.django_db(transaction=True)
def test_sp_produto_carrinho_delete(carrinho_id, produto_id):
    with connection.cursor() as cur:
        cur.execute("BEGIN;")
        try:
            cur.execute("INSERT INTO produto_carrinho (id_carrinho, id_produto, quantidade) VALUES (%s,%s,%s);",
                        [carrinho_id, produto_id, 1])
            cur.execute("CALL sp_produto_carrinho_delete(%s,%s);", [carrinho_id, produto_id])
            cur.execute("SELECT COUNT(*) FROM produto_carrinho WHERE id_carrinho=%s AND id_produto=%s;", [carrinho_id, produto_id])
            assert cur.fetchone()[0] == 0
        finally:
            cur.execute("ROLLBACK;")
