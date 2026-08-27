from django.db import models

class TorneoUsuario(models.Model):
    
    torneo = models.ForeignKey("Torneo", on_delete=models.CASCADE)
    usuario = models.ForeignKey("Usuario", on_delete=models.CASCADE)

    creador = models.BooleanField(null=False, default=False)
    eliminado = models.BooleanField(null=False, default=False)
