from django.db import models


class Rango(models.Model):
    class Color(models.TextChoices):
        BLANCO = "blanco", "Blanco"
        NEGRO = "negro", "Negro"
        ROSA = "rosa", "Rosa"
        ROSA_FUXIA = "rosa_fuxia", "Rosa fuxia"
        ROJO_CLARO = "rojo_claro", "Rojo claro"
        ROJO = "rojo", "Rojo"
        ROJO_OSCURO = "rojo_oscuro", "Rojo oscuro"
        VERDE_CLARO = "verde_claro", "Verde claro"
        VERDE_ESPERANZA = "verde_esperanza", "Verde esperanza"
        VERDE = "verde", "Verde"
        VERDE_OSCURO = "verde_oscuro", "Verde oscuro"
        AZUL_CLARO = "azul_claro", "Azul claro"
        AZUL = "azul", "Azul"
        AZUL_OSCURO = "azul_oscuro", "Azul oscuro"
        AZUL_CIAN = "azul_cian", "Azul cian"
        AMARILLO = "amarillo", "Amarillo"
        AMARILLO_DORADO = "amarillo_dorado", "Dorado"
        AMARILLO_NARANJA = "amarillo_naranja", "Amarillo anaranjado"
        NARANJA = "naranja", "Naranja"
        MORADO_CLARO = "morado_claro", "Púrpura"
        MORADO = "morado", "Morado"
        MORADO_OSCURO = "morado_oscuro", "Morado oscuro"
        GRIS = "gris", "Gris"
        PLATA = "gris_plata", "Plata"
        BRONCE = "marron_bronce", "Bronce"
        MARRON = "marron", "Marrón"
        
    nombre = models.CharField(max_length=25, unique=True, null=False, blank=False)
    color = models.CharField(
        max_length=20,
        choices=Color.choices,
        null=False,
        blank=False,
    )
    puntos_minimos = models.IntegerField(null=False, unique=True)
    puntos_maximos = models.IntegerField(null=False, unique=True)

    def __str__(self):
        return self.nombre, self.color