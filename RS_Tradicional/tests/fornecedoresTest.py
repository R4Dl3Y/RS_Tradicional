import pytest, django
from django.db import connection
django.setup()

@pytest.mark.django_db(transaction=True)
def test_sp_fornecedor_create():
    with connection.cursor() as cur:
        cur.execute("BEGIN;")
        try:
            args = ["FX2", "910000000", "fx2@example.com", "222333444", True, None, None, None]
            cur.execute("CALL sp_fornecedor_create(%s,%s,%s,%s,%s,%s,%s, %s);", args)
            new_id = cur.fetchone()[0]
            cur.execute("SELECT nome, isSingular FROM fornecedor WHERE id_fornecedor=%s;", [new_id])
            nome, singular = cur.fetchone()
            assert nome == "FX2" and singular is True
        finally:
            cur.execute("ROLLBACK;")

@pytest.mark.django_db(transaction=True)
def test_sp_fornecedor_get(fornecedor_id):
    with connection.cursor() as cur:
        cur.execute("BEGIN;")
        try:
            cur.execute("CALL sp_fornecedor_get(%s, %s);", [fornecedor_id, "curf"])
            cur.execute("FETCH ALL FROM curf;")
            rows = cur.fetchall()
            assert len(rows) == 1 and rows[0][0] == fornecedor_id
        finally:
            cur.execute("ROLLBACK;")

@pytest.mark.django_db(transaction=True)
def test_sp_fornecedor_update(fornecedor_id):
    with connection.cursor() as cur:
        cur.execute("BEGIN;")
        try:
            cur.execute("CALL sp_fornecedor_update(%s,%s,%s,%s,%s,%s,%s);",
                        [fornecedor_id, "Nome Novo", None, None, None, None, None])
            cur.execute("SELECT nome FROM fornecedor WHERE id_fornecedor=%s;", [fornecedor_id])
            assert cur.fetchone()[0] == "Nome Novo"
        finally:
            cur.execute("ROLLBACK;")

@pytest.mark.django_db(transaction=True)
def test_sp_fornecedor_delete(fornecedor_id):
    with connection.cursor() as cur:
        cur.execute("BEGIN;")
        try:
            cur.execute("CALL sp_fornecedor_delete(%s);", [fornecedor_id])
            cur.execute("SELECT COUNT(*) FROM fornecedor WHERE id_fornecedor=%s;", [fornecedor_id])
            assert cur.fetchone()[0] == 0
        finally:
            cur.execute("ROLLBACK;")
