import pytest, django
from django.db import connection
django.setup()

# --------- Estado_Carrinho ----------
@pytest.mark.django_db(transaction=True)
def test_sp_estado_carrinho_create():
    with connection.cursor() as cur:
        cur.execute("BEGIN;")
        try:
            cur.execute("CALL sp_estado_carrinho_create(%s, %s);", ["fechado", None])
            new_id = cur.fetchone()[0]
            cur.execute("SELECT descricao FROM estado_carrinho WHERE id_estado=%s;", [new_id])
            assert cur.fetchone()[0] == "fechado"
        finally:
            cur.execute("ROLLBACK;")

@pytest.mark.django_db(transaction=True)
def test_sp_estado_carrinho_get(estado_carrinho_id):
    with connection.cursor() as cur:
        cur.execute("BEGIN;")
        try:
            cur.execute("CALL sp_estado_carrinho_get(%s, %s);", [estado_carrinho_id, "curest"])
            cur.execute("FETCH ALL FROM curest;")
            rows = cur.fetchall()
            assert len(rows) == 1 and rows[0][0] == estado_carrinho_id
        finally:
            cur.execute("ROLLBACK;")

@pytest.mark.django_db(transaction=True)
def test_sp_estado_carrinho_update(estado_carrinho_id):
    with connection.cursor() as cur:
        cur.execute("BEGIN;")
        try:
            cur.execute("CALL sp_estado_carrinho_update(%s,%s);", [estado_carrinho_id, "em_pagamento"])
            cur.execute("SELECT descricao FROM estado_carrinho WHERE id_estado=%s;", [estado_carrinho_id])
            assert cur.fetchone()[0] == "em_pagamento"
        finally:
            cur.execute("ROLLBACK;")

@pytest.mark.django_db(transaction=True)
def test_sp_estado_carrinho_delete(estado_carrinho_id):
    with connection.cursor() as cur:
        cur.execute("BEGIN;")
        try:
            cur.execute("CALL sp_estado_carrinho_delete(%s);", [estado_carrinho_id])
            cur.execute("SELECT COUNT(*) FROM estado_carrinho WHERE id_estado=%s;", [estado_carrinho_id])
            assert cur.fetchone()[0] == 0
        finally:
            cur.execute("ROLLBACK;")

# --------- Carrinho ----------
@pytest.mark.django_db(transaction=True)
def test_sp_carrinho_create(utilizador_id):
    with connection.cursor() as cur:
        cur.execute("BEGIN;")
        try:
            cur.execute("CALL sp_carrinho_create(%s, %s, %s);", [utilizador_id, None, None])
            new_id = cur.fetchone()[0]
            cur.execute("SELECT id_utilizador FROM carrinho WHERE id_carrinho=%s;", [new_id])
            assert cur.fetchone()[0] == utilizador_id
        finally:
            cur.execute("ROLLBACK;")

@pytest.mark.django_db(transaction=True)
def test_sp_carrinho_get(carrinho_id):
    with connection.cursor() as cur:
        cur.execute("BEGIN;")
        try:
            cur.execute("CALL sp_carrinho_get(%s, %s);", [carrinho_id, "curcar"])
            cur.execute("FETCH ALL FROM curcar;")
            rows = cur.fetchall()
            assert len(rows) == 1 and rows[0][0] == carrinho_id
        finally:
            cur.execute("ROLLBACK;")

@pytest.mark.django_db(transaction=True)
def test_sp_carrinho_update(carrinho_id):
    with connection.cursor() as cur:
        cur.execute("BEGIN;")
        try:
            cur.execute("CALL sp_carrinho_update(%s,%s,%s);", [carrinho_id, None, None])
            cur.execute("SELECT id_carrinho FROM carrinho WHERE id_carrinho=%s;", [carrinho_id])
            assert cur.fetchone()[0] == carrinho_id
        finally:
            cur.execute("ROLLBACK;")

@pytest.mark.django_db(transaction=True)
def test_sp_carrinho_delete(carrinho_id):
    with connection.cursor() as cur:
        cur.execute("BEGIN;")
        try:
            cur.execute("CALL sp_carrinho_delete(%s);", [carrinho_id])
            cur.execute("SELECT COUNT(*) FROM carrinho WHERE id_carrinho=%s;", [carrinho_id])
            assert cur.fetchone()[0] == 0
        finally:
            cur.execute("ROLLBACK;")
