from django.db import models

class Mano(models.Model):
    
    partida = models.ForeignKey("Partida", on_delete=models.CASCADE)
    num = models.IntegerField(null=False, default=1)  # Número de la mano dentro de la partida