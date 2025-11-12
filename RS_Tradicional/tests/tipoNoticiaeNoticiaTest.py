import pytest, django
from django.db import connection
django.setup()

# --------- Tipo_Noticia ----------
@pytest.mark.django_db(transaction=True)
def test_sp_tipo_noticia_create():
    with connection.cursor() as cur:
        cur.execute("BEGIN;")
        try:
            cur.execute("CALL sp_tipo_noticia_create(%s, %s);", ["destaque", None])
            new_id = cur.fetchone()[0]
            cur.execute("SELECT nome FROM tipo_noticia WHERE id_tipo_noticia=%s;", [new_id])
            assert cur.fetchone()[0] == "destaque"
        finally:
            cur.execute("ROLLBACK;")

@pytest.mark.django_db(transaction=True)
def test_sp_tipo_noticia_get(tipo_noticia_id):
    with connection.cursor() as cur:
        cur.execute("BEGIN;")
        try:
            cur.execute("CALL sp_tipo_noticia_get(%s, %s);", [tipo_noticia_id, "curtn"])
            cur.execute("FETCH ALL FROM curtn;")
            rows = cur.fetchall()
            assert len(rows) == 1 and rows[0][0] == tipo_noticia_id
        finally:
            cur.execute("ROLLBACK;")

@pytest.mark.django_db(transaction=True)
def test_sp_tipo_noticia_update(tipo_noticia_id):
    with connection.cursor() as cur:
        cur.execute("BEGIN;")
        try:
            cur.execute("CALL sp_tipo_noticia_update(%s,%s);", [tipo_noticia_id, "campanha"])
            cur.execute("SELECT nome FROM tipo_noticia WHERE id_tipo_noticia=%s;", [tipo_noticia_id])
            assert cur.fetchone()[0] == "campanha"
        finally:
            cur.execute("ROLLBACK;")

@pytest.mark.django_db(transaction=True)
def test_sp_tipo_noticia_delete(tipo_noticia_id):
    with connection.cursor() as cur:
        cur.execute("BEGIN;")
        try:
            cur.execute("CALL sp_tipo_noticia_delete(%s);", [tipo_noticia_id])
            cur.execute("SELECT COUNT(*) FROM tipo_noticia WHERE id_tipo_noticia=%s;", [tipo_noticia_id])
            assert cur.fetchone()[0] == 0
        finally:
            cur.execute("ROLLBACK;")

# --------- Noticia ----------
@pytest.mark.django_db(transaction=True)
def test_sp_noticia_create(tipo_noticia_id, utilizador_id):
    with connection.cursor() as cur:
        cur.execute("BEGIN;")
        try:
            args = ["Titulo X", "Texto", tipo_noticia_id, utilizador_id, "2025-01-02", None]
            cur.execute("CALL sp_noticia_create(%s,%s,%s,%s,%s, %s);", args)
            new_id = cur.fetchone()[0]
            cur.execute("SELECT titulo, autor FROM noticia WHERE id_noticia=%s;", [new_id])
            titulo, autor = cur.fetchone()
            assert titulo == "Titulo X" and autor == utilizador_id
        finally:
            cur.execute("ROLLBACK;")

@pytest.mark.django_db(transaction=True)
def test_sp_noticia_get(noticia_id):
    with connection.cursor() as cur:
        cur.execute("BEGIN;")
        try:
            cur.execute("CALL sp_noticia_get(%s, %s);", [noticia_id, "curn"])
            cur.execute("FETCH ALL FROM curn;")
            rows = cur.fetchall()
            assert len(rows) == 1 and rows[0][0] == noticia_id
        finally:
            cur.execute("ROLLBACK;")

@pytest.mark.django_db(transaction=True)
def test_sp_noticia_update(noticia_id):
    with connection.cursor() as cur:
        cur.execute("BEGIN;")
        try:
            cur.execute("CALL sp_noticia_update(%s,%s,%s,%s,%s,%s);",
                        [noticia_id, "Novo Titulo", None, None, None, None])
            cur.execute("SELECT titulo FROM noticia WHERE id_noticia=%s;", [noticia_id])
            assert cur.fetchone()[0] == "Novo Titulo"
        finally:
            cur.execute("ROLLBACK;")

@pytest.mark.django_db(transaction=True)
def test_sp_noticia_delete(noticia_id):
    with connection.cursor() as cur:
        cur.execute("BEGIN;")
        try:
            cur.execute("CALL sp_noticia_delete(%s);", [noticia_id])
            cur.execute("SELECT COUNT(*) FROM noticia WHERE id_noticia=%s;", [noticia_id])
            assert cur.fetchone()[0] == 0
        finally:
            cur.execute("ROLLBACK;")
