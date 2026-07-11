from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractUser


class Usuario(AbstractUser):

    nombre = models.CharField(max_length=40, blank=False, null=False)
    puntuacion = models.IntegerField(default=0, null=False)
    imagen = models.TextField(blank=True, null=True, default=None, max_length=1000)

    # Ensure `createsuperuser` prompts for this required field.
    REQUIRED_FIELDS = ["email", "nombre"]

    def __str__(self):
        return self.nombre