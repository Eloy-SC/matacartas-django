from django.db import models


class Partida(models.Model):
    class LongitudPartida(models.TextChoices):
        CORTA = "corta", "Corta"
        NORMAL = "normal", "Normal"
        LARGA = "larga", "Larga"

    nombre = models.CharField(max_length=40, unique=True, null=False, blank=False)
    num_jugadores = models.IntegerField(null=False, default=2)
    privada = models.BooleanField(default=False)
    clave = models.CharField(max_length=20, null=True, blank=True)  # Clave en caso de partida privada

    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_inicio = models.DateTimeField(null=True, blank=True)
    fecha_fin = models.DateTimeField(null=True, blank=True)
    
    longitud = models.CharField(max_length=20, choices=LongitudPartida.choices, default=LongitudPartida.NORMAL)
    cartas_invencibles = models.BooleanField(default=True)  # Indica si las cartas invencibles están habilitadas
    tiempo_max_turno = models.IntegerField(null=False, default=90)  # Tiempo máximo por turno en segundos

    rango_minimo = models.ForeignKey("Rango", 
                                     on_delete=models.SET_NULL, 
                                     null=True, blank=True, 
                                     default=None)
    rango_maximo = models.ForeignKey("Rango", 
                                     on_delete=models.SET_NULL, 
                                     null=True, blank=True, 
                                     default=None)


