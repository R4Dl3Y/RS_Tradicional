import pytest, django
from django.db import connection

django.setup()

@pytest.mark.django_db(transaction=True)
def test_sp_tipo_utilizador_create():
    with connection.cursor() as cur:
        cur.execute("BEGIN;")
        try:
            cur.execute("CALL sp_tipo_utilizador_create(%s, %s);", ["admin", None])
            new_id = cur.fetchone()[0]
            cur.execute(
                "SELECT designacao FROM tipo_utilizador WHERE id_tipo_utilizador=%s;",
                [new_id]
            )
            assert cur.fetchone()[0] == "admin"
        finally:
            cur.execute("ROLLBACK;")

@pytest.mark.django_db(transaction=True)
def test_sp_tipo_utilizador_get(tipo_utilizador_id):
    with connection.cursor() as cur:
        cur.execute("BEGIN;")
        try:
            cur.execute("CALL sp_tipo_utilizador_get(%s, %s);", [tipo_utilizador_id, "cur1"])
            cur.execute("FETCH ALL FROM cur1;")
            rows = cur.fetchall()
            assert len(rows) == 1 and rows[0][0] == tipo_utilizador_id
        finally:
            cur.execute("ROLLBACK;")

@pytest.mark.django_db(transaction=True)
def test_sp_tipo_utilizador_update(tipo_utilizador_id):
    with connection.cursor() as cur:
        cur.execute("BEGIN;")
        try:
            cur.execute("CALL sp_tipo_utilizador_update(%s, %s);", [tipo_utilizador_id, "vip"])
            cur.execute("SELECT designacao FROM tipo_utilizador WHERE id_tipo_utilizador=%s;", [tipo_utilizador_id])
            assert cur.fetchone()[0] == "vip"
        finally:
            cur.execute("ROLLBACK;")

@pytest.mark.django_db(transaction=True)
def test_sp_tipo_utilizador_delete(tipo_utilizador_id):
    with connection.cursor() as cur:
        cur.execute("BEGIN;")
        try:
            cur.execute("CALL sp_tipo_utilizador_delete(%s);", [tipo_utilizador_id])
            cur.execute("SELECT COUNT(*) FROM tipo_utilizador WHERE id_tipo_utilizador=%s;", [tipo_utilizador_id])
            assert cur.fetchone()[0] == 0
        finally:
            cur.execute("ROLLBACK;")
