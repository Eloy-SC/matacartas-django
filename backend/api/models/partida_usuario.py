from django.db import models

class PartidaUsuario(models.Model):
    class ColorJugador(models.TextChoices):
        ROJO = "rojo", "Rojo"
        NARANJA = "naranja", "Naranja"
        AMARILLO = "amarillo", "Amarillo"
        VERDE = "verde", "Verde"
        AZUL = "azul", "Azul"
        MORADO = "morado", "Morado"

    partida = models.ForeignKey("Partida", on_delete=models.CASCADE)
    usuario = models.ForeignKey("Usuario", on_delete=models.CASCADE)
    creador = models.BooleanField(default=False)
    listo = models.BooleanField(default=False)
    color = models.CharField(
        max_length=8,
        choices=ColorJugador.choices,
        null=False,
        blank=False,
    )

    # Atributos in-game

    puntos = models.IntegerField(null=False, default=0)
    cartas = models.JSONField(default=list)  # Cartas poseidas por el jugador en mano
    carta_comodin = models.CharField(max_length=25, null=True, default=None)  # Carta que el jugador usa como comodín
    acumulador_kills = models.IntegerField(null=False, default=0)
    acumulador_deaths = models.IntegerField(null=False, default=0)