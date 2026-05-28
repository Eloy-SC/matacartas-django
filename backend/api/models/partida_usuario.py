from django.db import models

class PartidaUsuario(models.Model):

    id_partida = models.ForeignKey("Partida", on_delete=models.CASCADE)
    id_usuario = models.ForeignKey("Usuario", on_delete=models.CASCADE)
    creador = models.BooleanField(default=False)