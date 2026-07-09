from ..models.ronda import Ronda

def get_rondas_de_mano(mano_id):
    """
    Obtiene las rondas de una mano.
    """
    rondas = Ronda.objects.filter(mano_id=mano_id).order_by('num')
    res = []
    for ronda in rondas:
        res.append(ronda)
    return res