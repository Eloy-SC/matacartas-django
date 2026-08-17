

from ..models.resumen_mano import ResumenMano


def get_resumen_mano_by_mano_id(mano_id):
    return ResumenMano.objects.filter(mano_id=mano_id).order_by('-num').first()

def get_resumen_mano_by_id(id):
    return ResumenMano.objects.filter(id=id).order_by('-num').first()