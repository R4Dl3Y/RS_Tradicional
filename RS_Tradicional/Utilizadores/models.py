# Utilizadores/models.py
from django.db import models
from django.core.validators import RegexValidator, EmailValidator


class TipoUtilizador(models.Model):
    id_tipo_utilizador = models.AutoField(
        primary_key=True,
        db_column='id_tipo_utilizador'
    )
    designacao = models.CharField(
        max_length=50,
        null=False,
        blank=False
    )

    class Meta:
        db_table = 'tipo_utilizador'   # CREATE TABLE Tipo_Utilizador -> em PostgreSQL fica "tipo_utilizador"
        managed = False
        verbose_name = 'Tipo de Utilizador'
        verbose_name_plural = 'Tipos de Utilizador'

    def __str__(self):
        return self.designacao


class Utilizador(models.Model):
    id_utilizador = models.AutoField(
        primary_key=True,
        db_column='id_utilizador'
    )

    nome = models.CharField(
        max_length=100,
        null=False,
        blank=False
    )

    email = models.CharField(
        max_length=255,
        validators=[EmailValidator(message="Email inválido.")],
        null=False,
        blank=False
    )

    password = models.CharField(
        max_length=255,
        null=False,
        blank=False
    )

    morada = models.TextField(
        blank=True,
        null=True
    )

    nif = models.CharField(
        max_length=9,
        validators=[
            RegexValidator(
                regex=r'^\d{9}$',
                message='O NIF deve ter exatamente 9 dígitos numéricos.'
            )
        ],
        null=False,
        blank=False
    )

    id_tipo_utilizador = models.ForeignKey(
        TipoUtilizador,
        on_delete=models.SET_NULL,
        db_column='id_tipo_utilizador',
        null=True,
        blank=True,
        related_name='utilizadores',
    )

    class Meta:
        db_table = 'utilizador'   # CREATE TABLE Utilizador -> em PostgreSQL fica "utilizador"
        managed = False
        verbose_name = 'Utilizador'
        verbose_name_plural = 'Utilizadores'

    def __str__(self):
        return self.nome
