from django.db import models


class Torneo(models.Model):

    nombre = models.CharField(max_length=40, unique=True, null=False, blank=False)

    num_jug_fin = models.IntegerField(null=False, default=3) # Num jugadores de la partida de la final
    num_jug_sem = models.IntegerField(null=False, default=3) # Num jugadores de las partidas de las semis
    num_jug_cua = models.IntegerField(null=True, default=3) # Num jugadores de las partidas de los cuartos, null=no hay cuartos
    num_jug_oct = models.IntegerField(null=True, default=3) # Num jugadores de las partidas de los octavos, null=no hay octavos

    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_inicio = models.DateTimeField(null=True, blank=True)
    fecha_fin = models.DateTimeField(null=True, blank=True)

    desempate_mayor_punt = models.BooleanField(null=False, default=True) # True=desempate por mayor puntuación, False=desempate al azar
