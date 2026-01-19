from django.db import models
from Utilizadores.models import Utilizador
from Produtos.models import Produto


class Encomenda(models.Model):
    id_encomenda = models.AutoField(
        primary_key=True,
        db_column="id_encomenda",
    )
    data_encomenda = models.DateField(db_column="data_encomenda")
    id_utilizador = models.ForeignKey(
        Utilizador,
        on_delete=models.CASCADE,
        db_column="id_utilizador",
        related_name="encomendas",
    )
    estado_encomenda = models.CharField(
        max_length=64,
        db_column="estado_encomenda",
    )

    class Meta:
        db_table = "encomenda"
        managed = False

    def __str__(self):
        return f"Encomenda #{self.id_encomenda} - {self.id_utilizador.nome}"


class EncomendaProduto(models.Model):
    id = models.AutoField(
        primary_key=True,
        db_column="id"
    )
    id_encomenda = models.ForeignKey(
        Encomenda,
        on_delete=models.CASCADE,
        db_column="id_encomenda",
        related_name="linhas",
    )
    id_produto = models.ForeignKey(
        Produto,
        on_delete=models.CASCADE,
        db_column="id_produto",
        related_name="linhas_encomenda",
    )
    quantidade = models.IntegerField(
        default=1,
        db_column="quantidade",
    )

    class Meta:
        db_table = "encomendas_produtos"
        managed = False
        unique_together = (("id_encomenda", "id_produto"),)

    def __str__(self):
        return f"Encomenda #{self.id_encomenda_id} - Produto {self.id_produto_id} (x{self.quantidade})"
