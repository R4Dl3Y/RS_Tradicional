import pytest, django
from django.db import connection
django.setup()

@pytest.mark.django_db(transaction=True)
def test_sp_imagem_noticia_create(noticia_id):
    with connection.cursor() as cur:
        cur.execute("BEGIN;")
        try:
            cur.execute("CALL sp_imagem_noticia_create(%s,%s,%s);", [noticia_id, "https://img/x.png", None])
            iid = cur.fetchone()[0]
            cur.execute("SELECT uri, id_noticia FROM imagem_noticia WHERE id_imagem=%s;", [iid])
            uri, nid = cur.fetchone()
            assert uri == "https://img/x.png" and nid == noticia_id
        finally:
            cur.execute("ROLLBACK;")

@pytest.mark.django_db(transaction=True)
def test_sp_imagem_noticia_get(noticia_id):
    with connection.cursor() as cur:
        cur.execute("BEGIN;")
        try:
            cur.execute("INSERT INTO imagem_noticia (id_noticia, uri) VALUES (%s,%s) RETURNING id_imagem;",
                        [noticia_id, "https://img/tmp.png"])
            iid = cur.fetchone()[0]
            cur.execute("CALL sp_imagem_noticia_get(%s, %s);", [iid, "curin"])
            cur.execute("FETCH ALL FROM curin;")
            rows = cur.fetchall()
            assert len(rows) == 1 and rows[0][0] == iid
        finally:
            cur.execute("ROLLBACK;")

@pytest.mark.django_db(transaction=True)
def test_sp_imagem_noticia_update(noticia_id):
    with connection.cursor() as cur:
        cur.execute("BEGIN;")
        try:
            cur.execute("INSERT INTO imagem_noticia (id_noticia, uri) VALUES (%s,%s) RETURNING id_imagem;",
                        [noticia_id, "https://img/old.png"])
            iid = cur.fetchone()[0]
            cur.execute("CALL sp_imagem_noticia_update(%s,%s,%s);", [iid, None, "https://img/new.png"])
            cur.execute("SELECT uri FROM imagem_noticia WHERE id_imagem=%s;", [iid])
            assert cur.fetchone()[0] == "https://img/new.png"
        finally:
            cur.execute("ROLLBACK;")

@pytest.mark.django_db(transaction=True)
def test_sp_imagem_noticia_delete(noticia_id):
    with connection.cursor() as cur:
        cur.execute("BEGIN;")
        try:
            cur.execute("INSERT INTO imagem_noticia (id_noticia, uri) VALUES (%s,%s) RETURNING id_imagem;",
                        [noticia_id, "https://img/del.png"])
            iid = cur.fetchone()[0]
            cur.execute("CALL sp_imagem_noticia_delete(%s);", [iid])
            cur.execute("SELECT COUNT(*) FROM imagem_noticia WHERE id_imagem=%s;", [iid])
            assert cur.fetchone()[0] == 0
        finally:
            cur.execute("ROLLBACK;")
