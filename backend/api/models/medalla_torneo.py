from django.db import models


class MedallaTorneo(models.Model):
    medalla = models.ForeignKey("Medalla", on_delete=models.CASCADE)
    torneo = models.ForeignKey("Torneo", on_delete=models.CASCADE)
    puesto = models.IntegerField(null=False, blank=False)
    