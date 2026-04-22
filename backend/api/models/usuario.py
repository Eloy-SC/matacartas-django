# encoding:utf-8

from django.db import models


class Usuario(models.Model):
    class Rol(models.TextChoices):
        ADMIN = "ADMIN", "ADMIN"
        PLAYER = "PLAYER", "PLAYER"

    id = models.BigAutoField(primary_key=True)
    username = models.CharField(max_length=30, unique=True)
    password = models.CharField(max_length=30)
    nombre = models.CharField(max_length=50)
    rol = models.CharField(max_length=6, choices=Rol.choices, default=Rol.PLAYER)

    def __str__(self):
        return self.username
