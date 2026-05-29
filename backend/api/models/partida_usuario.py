from django.db import models

class PartidaUsuario(models.Model):

    partida = models.ForeignKey("Partida", on_delete=models.CASCADE)
    usuario = models.ForeignKey("Usuario", on_delete=models.CASCADE)
    creador = models.BooleanField(default=False)