import pytest, django
from django.db import connection
django.setup()

@pytest.mark.django_db(transaction=True)
def test_sp_utilizador_create(tipo_utilizador_id):
    with connection.cursor() as cur:
        cur.execute("BEGIN;")
        try:
            args = ["Bob", "bob@example.com", "pw", "Rua B", "111222333", None, tipo_utilizador_id, None]
            cur.execute("CALL sp_utilizador_create(%s,%s,%s,%s,%s,%s,%s, %s);", args)
            new_id = cur.fetchone()[0]
            cur.execute("SELECT email, id_tipo_utilizador FROM utilizador WHERE id_utilizador=%s;", [new_id])
            email, tipo = cur.fetchone()
            assert email == "bob@example.com" and tipo == tipo_utilizador_id
        finally:
            cur.execute("ROLLBACK;")

@pytest.mark.django_db(transaction=True)
def test_sp_utilizador_get(utilizador_id):
    with connection.cursor() as cur:
        cur.execute("BEGIN;")
        try:
            cur.execute("CALL sp_utilizador_get(%s, %s);", [utilizador_id, "curu"])
            cur.execute("FETCH ALL FROM curu;")
            rows = cur.fetchall()
            assert len(rows) == 1 and rows[0][0] == utilizador_id
        finally:
            cur.execute("ROLLBACK;")

@pytest.mark.django_db(transaction=True)
def test_sp_utilizador_update(utilizador_id):
    with connection.cursor() as cur:
        cur.execute("BEGIN;")
        try:
            cur.execute("""
                CALL sp_utilizador_update(%s,%s,%s,%s,%s,%s,%s,%s);
            """, [utilizador_id, "Alice Nova", None, None, None, None, None, None])
            cur.execute("SELECT nome FROM utilizador WHERE id_utilizador=%s;", [utilizador_id])
            assert cur.fetchone()[0] == "Alice Nova"
        finally:
            cur.execute("ROLLBACK;")

@pytest.mark.django_db(transaction=True)
def test_sp_utilizador_delete(utilizador_id):
    with connection.cursor() as cur:
        cur.execute("BEGIN;")
        try:
            cur.execute("CALL sp_utilizador_delete(%s);", [utilizador_id])
            cur.execute("SELECT COUNT(*) FROM utilizador WHERE id_utilizador=%s;", [utilizador_id])
            assert cur.fetchone()[0] == 0
        finally:
            cur.execute("ROLLBACK;")
