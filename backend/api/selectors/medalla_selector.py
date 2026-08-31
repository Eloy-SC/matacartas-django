from ..models.medalla_torneo import MedallaTorneo

from ..models.recompensa import Medalla


def get_medalla_by_id(medalla_id):
    return Medalla.objects.filter(id=medalla_id).first()


def get_medalla_by_nombre(nombre):
    return Medalla.objects.filter(nombre=nombre).first()

def get_medalla_by_id(medalla_id):
    return Medalla.objects.filter(id=medalla_id).values("id", "nombre", "categoria", "imagen").first()

def get_medallas_by_torneo_id(torneo_id):
    medallas_torneo = MedallaTorneo.objects.filter(torneo__id=torneo_id).order_by("puesto")
    medallas = [medalla_torneo.medalla for medalla_torneo in medallas_torneo]
    return medallas

def list_medallas():
    return Medalla.objects.all().values("id", "nombre", "categoria", "imagen").order_by("nombre")