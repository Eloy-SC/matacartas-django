from django.db import models


class Partida(models.Model):
    class LongitudPartida(models.TextChoices):
        CORTA = "corta", "Corta"
        NORMAL = "normal", "Normal"
        LARGA = "larga", "Larga"


    # Configuracion de la partida    

    nombre = models.CharField(max_length=40, unique=True, null=False, blank=False)
    num_jugadores = models.IntegerField(null=False, default=2)
    privada = models.BooleanField(default=False)
    clave = models.CharField(max_length=20, unique=True, null=True, blank=True)  # Clave en caso de partida privada

    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_inicio = models.DateTimeField(null=True, blank=True)
    fecha_fin = models.DateTimeField(null=True, blank=True)
    
    longitud = models.CharField(max_length=20, choices=LongitudPartida.choices, default=LongitudPartida.NORMAL)
    cartas_especiales = models.BooleanField(default=True)  # Indica si las cartas especiales están habilitadas
    tickets = models.BooleanField(default=True)  # Indica si los tickets están habilitados
    tiempo_max_turno = models.IntegerField(null=False, default=90)  # Tiempo máximo por turno en segundos

    rango_minimo = models.ForeignKey("Rango", 
                                     on_delete=models.SET_NULL, 
                                     null=True, blank=True, 
                                     default=None)
    rango_maximo = models.ForeignKey("Rango", 
                                     on_delete=models.SET_NULL, 
                                     null=True, blank=True, 
                                     default=None)
    
    # Atributos in-game

    baraja = models.JSONField(default=list)  # Representación de la baraja de cartas
    disposicion_jugadores = models.JSONField(default=list)  # Representación de la disposición de los jugadores en la partida
    turno_actual = models.CharField(max_length=8, null=True)  # Color del jugador que tiene el turno actual

