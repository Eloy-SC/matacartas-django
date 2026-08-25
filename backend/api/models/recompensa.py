from django.db import models


class Recompensa(models.Model):

    nombre = models.CharField(max_length=40, unique=True, null=False, blank=False)
    imagen = models.TextField(blank=True, null=True, default=None, max_length=1000)

    class Meta:
        abstract = True

class Medalla(Recompensa):
    class CategoriaMedalla(models.TextChoices):
        ORO = "oro", "Oro"
        PLATA = "plata", "Plata"
        BRONCE = "bronce", "Bronce"

    categoria = models.CharField(max_length=20, choices=CategoriaMedalla.choices, default=CategoriaMedalla.BRONCE)
