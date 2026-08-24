from django.db import models

class TorneoUsuario(models.Model):
    
    torneo = models.ForeignKey("Torneo", on_delete=models.CASCADE)
    usuario = models.ForeignKey("Usuario", on_delete=models.CASCADE)

    creador = models.BooleanField(null=False, default=False)
    identificador = models.IntegerField(unique=True, null=False, blank=False) # Identificador del jugador dentro del torneo
    
