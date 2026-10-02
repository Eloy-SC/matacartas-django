from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager


class UsuarioManager(UserManager):

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields["email_verificado"] = True
        return super().create_superuser(username, email, password, **extra_fields)


class Usuario(AbstractUser):

    objects = UsuarioManager()

    nombre = models.CharField(max_length=40, blank=False, null=False)
    puntuacion = models.IntegerField(default=0, null=False)
    imagen = models.TextField(blank=True, null=True, default=None, max_length=1000)
    email_verificado = models.BooleanField(default=False)

    # Ensure `createsuperuser` prompts for this required field.
    REQUIRED_FIELDS = ["email", "nombre"]

    def __str__(self):
        return self.nombre