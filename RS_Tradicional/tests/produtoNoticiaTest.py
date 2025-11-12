import pytest, django
from django.db import connection
django.setup()

@pytest.mark.django_db(transaction=True)
def test_sp_produto_noticia_create(noticia_id, produto_id):
    with connection.cursor() as cur:
        cur.execute("BEGIN;")
        try:
            cur.execute("CALL sp_produto_noticia_create(%s,%s);", [noticia_id, produto_id])
            cur.execute("SELECT COUNT(*) FROM produto_noticia WHERE id_noticia=%s AND id_produto=%s;",
                        [noticia_id, produto_id])
            assert cur.fetchone()[0] == 1
        finally:
            cur.execute("ROLLBACK;")

@pytest.mark.django_db(transaction=True)
def test_sp_produto_noticia_get(noticia_id, produto_id):
    with connection.cursor() as cur:
        cur.execute("BEGIN;")
        try:
            cur.execute("INSERT INTO produto_noticia (id_noticia, id_produto) VALUES (%s,%s) ON CONFLICT DO NOTHING;",
                        [noticia_id, produto_id])
            cur.execute("CALL sp_produto_noticia_get(%s,%s,%s);", [noticia_id, produto_id, "curpn"])
            cur.execute("FETCH ALL FROM curpn;")
            rows = cur.fetchall()
            assert len(rows) == 1 and rows[0][0] == noticia_id and rows[0][1] == produto_id
        finally:
            cur.execute("ROLLBACK;")

@pytest.mark.django_db(transaction=True)
def test_sp_produto_noticia_delete(noticia_id, produto_id):
    with connection.cursor() as cur:
        cur.execute("BEGIN;")
        try:
            cur.execute("INSERT INTO produto_noticia (id_noticia, id_produto) VALUES (%s,%s) ON CONFLICT DO NOTHING;",
                        [noticia_id, produto_id])
            cur.execute("CALL sp_produto_noticia_delete(%s,%s);", [noticia_id, produto_id])
            cur.execute("SELECT COUNT(*) FROM produto_noticia WHERE id_noticia=%s AND id_produto=%s;",
                        [noticia_id, produto_id])
            assert cur.fetchone()[0] == 0
        finally:
            cur.execute("ROLLBACK;")
