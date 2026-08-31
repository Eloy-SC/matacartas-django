from django.db import models


class Torneo(models.Model):
    class LongitudPartidaDeTorneo(models.TextChoices):
        EXPRESS = "express", "Express"
        CORTA = "corta", "Corta"
        NORMAL = "normal", "Normal"
        LARGA = "larga", "Larga"

    nombre = models.CharField(max_length=39, unique=True, null=False, blank=False)

    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_inicio = models.DateTimeField(null=True, blank=True)
    fecha_fin = models.DateTimeField(null=True, blank=True)

    rango_minimo = models.ForeignKey("Rango", 
                                         on_delete=models.SET_NULL, 
                                         null=True, blank=True, 
                                         default=None,
                                         related_name="torneos_rango_minimo")
    rango_maximo = models.ForeignKey("Rango", 
                                         on_delete=models.SET_NULL, 
                                         null=True, blank=True, 
                                         default=None,
                                         related_name="torneos_rango_maximo")

    num_jug_fin = models.IntegerField(null=False, default=3) # Num jugadores de la partida de la final
    num_jug_sem = models.IntegerField(null=False, default=3) # Num jugadores de las partidas de las semis
    num_jug_cua = models.IntegerField(null=True, default=3) # Num jugadores de las partidas de los cuartos, null=no hay cuartos
    num_jug_oct = models.IntegerField(null=True, default=3) # Num jugadores de las partidas de los octavos, null=no hay octavos

    # Otra config de partida
    partidas_longitud = models.CharField(max_length=20, choices=LongitudPartidaDeTorneo.choices, default=LongitudPartidaDeTorneo.NORMAL)
    partidas_cartas_especiales = models.BooleanField(default=True)
    partidas_tickets = models.BooleanField(default=True)
    partidas_tiempo_max_turno = models.IntegerField(null=False, default=90)

    desempate_mayor_punt = models.BooleanField(null=False, default=True) # True=desempate por mayor puntuación, False=desempate al azar
