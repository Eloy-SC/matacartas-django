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