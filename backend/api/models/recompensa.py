from django.db import models


class Recompensa(models.Model):

    nombre = models.CharField(max_length=40, unique=True, null=False, blank=False)
    imagen = models.TextField(blank=True, null=True, default=None, max_length=1000)

    class Meta:
        abstract = False # Esta clase no se creará como tabla en la base de datos

class Medalla(Recompensa):
    pass
