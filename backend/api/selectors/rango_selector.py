from ..models import Rango

def get_rango_by_puntos(puntos):
    return Rango.objects.filter(puntos_minimos__lte=puntos, puntos_maximos__gte=puntos).first()

def get_rango_by_min_puntos(puntos):
    return Rango.objects.filter(puntos_minimos=puntos).first()

def get_rango_by_max_puntos(puntos):
    return Rango.objects.filter(puntos_maximos=puntos).first()

def get_rangos_parejas_valores():
    rangos = Rango.objects.all().order_by("puntos_minimos")
    return [(rango.puntos_minimos, rango.puntos_maximos) for rango in rangos]
