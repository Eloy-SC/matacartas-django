from ..models.recompensa import Medalla


def get_medalla_by_id(medalla_id):
    return Medalla.objects.filter(id=medalla_id).first()


def get_medalla_by_nombre(nombre):
    return Medalla.objects.filter(nombre=nombre).first()
