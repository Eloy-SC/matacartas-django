from django.db import models

class Ronda(models.Model):
    
    mano = models.ForeignKey("Mano", on_delete=models.CASCADE)
    num = models.IntegerField(null=False, default=0)  # Número de la ronda dentro de la mano, 0=todo lo anterior a las 3 rondas, 4=ronda comodin