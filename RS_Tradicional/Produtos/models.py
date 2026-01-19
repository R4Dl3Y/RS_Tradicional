# Produtos/models.py
from django.db import models
from Utilizadores.models import Utilizador  # se precisares no futuro
# from ... importa TipoProduto, Fornecedor se estiverem aqui também


class TipoProduto(models.Model):
    id_tipo_produto = models.AutoField(primary_key=True, db_column="id_tipo_produto")
    designacao = models.CharField(max_length=100)

    class Meta:
        db_table = "tipo_produto"
        managed = False

    def __str__(self):
        return self.designacao


class Fornecedor(models.Model):
    id_fornecedor = models.AutoField(primary_key=True, db_column="id_fornecedor")
    nome = models.CharField(max_length=100)
    contacto = models.CharField(max_length=20)
    email = models.CharField(max_length=255)
    nif = models.CharField(max_length=9)
    isSingular = models.BooleanField(db_column="issingular")
    morada = models.TextField(null=True, blank=True)
    imagem_fornecedor = models.TextField(null=True, blank=True)

    class Meta:
        db_table = "fornecedor"
        managed = False

    def __str__(self):
        return self.nome


class Produto(models.Model):
    id_produto = models.AutoField(primary_key=True, db_column="id_produto")
    nome = models.CharField(max_length=255)
    descricao = models.TextField(null=True, blank=True)
    preco = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField()
    is_approved = models.BooleanField(default=False, db_column="is_approved")
    estado_produto = models.CharField(max_length=64, db_column="estado_produto")
    id_tipo_produto = models.ForeignKey(
        TipoProduto,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        db_column="id_tipo_produto",
    )
    id_fornecedor = models.ForeignKey(
        Fornecedor,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        db_column="id_fornecedor",
    )

    class Meta:
        db_table = "produto"
        managed = False

    def __str__(self):
        return self.nome
