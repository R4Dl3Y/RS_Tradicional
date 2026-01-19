# Noticias/models.py
from django.db import models
from Utilizadores.models import Utilizador
from Produtos.models import Produto


class TipoNoticia(models.Model):
    id_tipo_noticia = models.AutoField(
        primary_key=True,
        db_column="id_tipo_noticia"
    )
    nome = models.CharField(max_length=50, db_column="nome")

    class Meta:
        db_table = "tipo_noticia"
        managed = False
        verbose_name = "Tipo de Notícia"
        verbose_name_plural = "Tipos de Notícia"

    def __str__(self):
        return self.nome


class Noticia(models.Model):
    id_noticia = models.AutoField(
        primary_key=True,
        db_column="id_noticia"
    )
    titulo = models.CharField(max_length=200, db_column="titulo")
    conteudo = models.CharField(max_length=255, db_column="conteudo")
    id_tipo_noticia = models.ForeignKey(
        TipoNoticia,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="id_tipo_noticia",
        related_name="noticias",
    )
    autor = models.ForeignKey(
        Utilizador,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="autor",
        related_name="noticias",
    )
    data_publicacao = models.DateField(db_column="data_publicacao")

    class Meta:
        db_table = "noticia"
        managed = False
        verbose_name = "Notícia"
        verbose_name_plural = "Notícias"

    def __str__(self):
        return self.titulo


class ImagemNoticia(models.Model):
    id_imagem = models.AutoField(
        primary_key=True,
        db_column="id_imagem"
    )
    id_noticia = models.ForeignKey(
        Noticia,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="id_noticia",
        related_name="imagens",
    )
    uri = models.TextField(db_column="uri")

    class Meta:
        db_table = "imagem_noticia"
        managed = False
        verbose_name = "Imagem de Notícia"
        verbose_name_plural = "Imagens de Notícia"

    def __str__(self):
        return f"Imagem #{self.id_imagem} da notícia {self.id_noticia_id}"


class ProdutoNoticia(models.Model):
    id_noticia = models.ForeignKey(
        Noticia,
        on_delete=models.CASCADE,
        db_column="id_noticia",
    )
    id_produto = models.ForeignKey(
        Produto,
        on_delete=models.CASCADE,
        db_column="id_produto",
    )

    class Meta:
        db_table = "produto_noticia"
        managed = False
        unique_together = (("id_noticia", "id_produto"),)
        verbose_name = "Produto em Notícia"
        verbose_name_plural = "Produtos em Notícia"

    def __str__(self):
        return f"Notícia {self.id_noticia_id} · Produto {self.id_produto_id}"
