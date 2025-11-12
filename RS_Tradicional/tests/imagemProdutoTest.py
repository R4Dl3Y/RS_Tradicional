import pytest, django
from django.db import connection
django.setup()

@pytest.mark.django_db(transaction=True)
def test_sp_imagem_produto_create(produto_id):
    with connection.cursor() as cur:
        cur.execute("BEGIN;")
        try:
            cur.execute("CALL sp_imagem_produto_create(%s,%s,%s);", [produto_id, "/img/p1.png", None])
            new_id = cur.fetchone()[0]
            cur.execute("SELECT caminho, id_produto FROM imagem_produto WHERE id_imagem=%s;", [new_id])
            caminho, pid = cur.fetchone()
            assert caminho == "/img/p1.png" and pid == produto_id
        finally:
            cur.execute("ROLLBACK;")

@pytest.mark.django_db(transaction=True)
def test_sp_imagem_produto_get(produto_id):
    with connection.cursor() as cur:
        cur.execute("BEGIN;")
        try:
            cur.execute("INSERT INTO imagem_produto (id_produto, caminho) VALUES (%s, %s) RETURNING id_imagem;",
                        [produto_id, "/img/tmp.png"])
            iid = cur.fetchone()[0]

            cur.execute("CALL sp_imagem_produto_get(%s, %s);", [iid, "curip"])
            cur.execute("FETCH ALL FROM curip;")
            rows = cur.fetchall()
            assert len(rows) == 1 and rows[0][0] == iid
        finally:
            cur.execute("ROLLBACK;")

@pytest.mark.django_db(transaction=True)
def test_sp_imagem_produto_update(produto_id):
    with connection.cursor() as cur:
        cur.execute("BEGIN;")
        try:
            cur.execute("INSERT INTO imagem_produto (id_produto, caminho) VALUES (%s,%s) RETURNING id_imagem;",
                        [produto_id, "/img/old.png"])
            iid = cur.fetchone()[0]
            cur.execute("CALL sp_imagem_produto_update(%s,%s,%s);", [iid, None, "/img/new.png"])
            cur.execute("SELECT caminho FROM imagem_produto WHERE id_imagem=%s;", [iid])
            assert cur.fetchone()[0] == "/img/new.png"
        finally:
            cur.execute("ROLLBACK;")

@pytest.mark.django_db(transaction=True)
def test_sp_imagem_produto_delete(produto_id):
    with connection.cursor() as cur:
        cur.execute("BEGIN;")
        try:
            cur.execute("INSERT INTO imagem_produto (id_produto, caminho) VALUES (%s,%s) RETURNING id_imagem;",
                        [produto_id, "/img/del.png"])
            iid = cur.fetchone()[0]
            cur.execute("CALL sp_imagem_produto_delete(%s);", [iid])
            cur.execute("SELECT COUNT(*) FROM imagem_produto WHERE id_imagem=%s;", [iid])
            assert cur.fetchone()[0] == 0
        finally:
            cur.execute("ROLLBACK;")
