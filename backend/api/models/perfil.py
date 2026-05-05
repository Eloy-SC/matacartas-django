from django.conf import settings
from django.db import models


class Perfil(models.Model):

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="perfil",
    )
    nombre = models.CharField(max_length=30, blank=False, null=False)
    puntuacion = models.IntegerField(default=0)
    imagen = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre
