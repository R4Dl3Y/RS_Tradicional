from django.core.management.base import BaseCommand
from django.db import connection
from decimal import Decimal
from datetime import date

from Core.mongo import get_mongo_db


def fetchall_dicts(sql, params=None):
    with connection.cursor() as cur:
        cur.execute(sql, params or [])
        cols = [c[0] for c in cur.description]
        return [dict(zip(cols, row)) for row in cur.fetchall()]


class Command(BaseCommand):
    help = "Sync reports data from Postgres views to MongoDB"

    def handle(self, *args, **options):
        db = get_mongo_db()
        orders = db["orders"]

        # Cabeçalhos (admin) - exclui Carrinho
        encomendas = fetchall_dicts("""
            SELECT
                id_encomenda,
                data_encomenda,
                estado_encomenda,
                id_utilizador,
                utilizador_nome,
                utilizador_email
            FROM vw_admin_encomendas
            WHERE estado_encomenda <> 'Carrinho'
        """)

        # Linhas (produto + preço + quantidade)
        linhas = fetchall_dicts("""
            SELECT
                id_encomenda,
                id_produto,
                quantidade,
                produto_nome,
                produto_preco
            FROM vw_encomendas_produtos
        """)

        # Produto -> fornecedor
        prod_map = fetchall_dicts("""
            SELECT id_produto, id_fornecedor
            FROM vw_admin_produtos
        """)
        prod_to_fornecedor = {p["id_produto"]: p["id_fornecedor"] for p in prod_map}

        # Fornecedor -> nome (para top fornecedores no dashboard)
        forn_map = fetchall_dicts("""
            SELECT id_fornecedor, nome
            FROM vw_fornecedores
        """)
        fornecedor_nome = {f["id_fornecedor"]: f["nome"] for f in forn_map}

        # Agrupar linhas por encomenda
        linhas_por_encomenda = {}
        for l in linhas:
            eid = l["id_encomenda"]
            preco = Decimal(str(l["produto_preco"])) if l["produto_preco"] is not None else Decimal("0")
            qtd = int(l["quantidade"] or 0)
            subtotal = float(preco * qtd)

            fid = prod_to_fornecedor.get(l["id_produto"])
            linhas_por_encomenda.setdefault(eid, []).append({
                "id_produto": l["id_produto"],
                "nome": l["produto_nome"],
                "preco": float(preco),
                "quantidade": qtd,
                "subtotal": subtotal,
                "id_fornecedor": fid,
                "fornecedor_nome": fornecedor_nome.get(fid),
            })

        # Upsert no Mongo
        for e in encomendas:
            eid = e["id_encomenda"]
            doc_linhas = linhas_por_encomenda.get(eid, [])
            total = sum(x["subtotal"] for x in doc_linhas)

            data_enc = e["data_encomenda"]
            # guardar data como string para facilitar group-by no Mongo
            data_str = data_enc.isoformat() if isinstance(data_enc, date) else str(data_enc)

            doc = {
                "_id": eid,
                "id_encomenda": eid,
                "data": data_str,
                "estado": e["estado_encomenda"],
                "cliente": {
                    "id": e["id_utilizador"],
                    "nome": e["utilizador_nome"],
                    "email": e["utilizador_email"],
                },
                "linhas": doc_linhas,
                "total": float(total),
            }

            orders.update_one({"_id": eid}, {"$set": doc}, upsert=True)

        # Índices úteis
        orders.create_index("data")
        orders.create_index("estado")
        orders.create_index("cliente.id")
        orders.create_index("linhas.id_produto")
        orders.create_index("linhas.id_fornecedor")

        self.stdout.write(self.style.SUCCESS("Sync Mongo concluído com sucesso."))
