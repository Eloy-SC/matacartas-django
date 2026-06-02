from ..models.rango import Rango

def get_rango_by_puntos(puntos):
    return Rango.objects.filter(puntos_minimos__lte=puntos, puntos_maximos__gte=puntos).first()

def get_rango_by_id(rango_id):
    return Rango.objects.filter(id=rango_id).first()

def get_rango_by_min_puntos(puntos):
    return Rango.objects.filter(puntos_minimos=puntos).first()

def get_rango_by_max_puntos(puntos):
    return Rango.objects.filter(puntos_maximos=puntos).first()

def get_rangos_parejas_valores():
    rangos = Rango.objects.all().order_by("puntos_minimos")
    return [(rango.puntos_minimos, rango.puntos_maximos) for rango in rangos]

def get_rangos_parejas_valores_exclude_rango(rango_id):
    rangos = Rango.objects.exclude(id=rango_id).order_by("puntos_minimos")
    return [(rango.puntos_minimos, rango.puntos_maximos) for rango in rangos]

def get_rango_by_color(color):
    return Rango.objects.filter(color=color).first()
