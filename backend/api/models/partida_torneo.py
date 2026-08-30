from django.db import models

class PartidaTorneo(models.Model):
    class FasePartida(models.TextChoices):
        OCTAVOS = "octavos", "Octavos"
        CUARTOS = "cuartos", "Cuartos"
        SEMIFINAL = "semifinal", "Semifinal"
        FINAL = "final", "Final"

    partida = models.ForeignKey("Partida", on_delete=models.CASCADE)
    torneo = models.ForeignKey("Torneo", on_delete=models.CASCADE)

    fase = models.CharField(max_length=20, choices=FasePartida.choices, default=FasePartida.CUARTOS)
    lado = models.IntegerField(null=False, default=0)  # Sólo valores 0 y 1
    pareja = models.IntegerField(null=False, default=0)  # El número de la pareja dentro del lado y de la fase.

    posiciones_finales = models.JSONField(default=dict) # Claves: identificador del jugador en el torneo, Valor: puntos en partida
