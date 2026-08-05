from ..models.catalogo_cartas import CATALOGO

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

def get_ronda_cambios(mano_id):
    """
    Obtiene la ronda de cambios de una mano.
    """
    return Ronda.objects.filter(mano_id=mano_id, num=0).first()

def get_jugador_lanzador_carta_mayor_fuerza(ronda_id):
    """
    Obtiene el jugador que lanzó la carta de mayor fuerza en una ronda.
    """
    ronda = Ronda.objects.filter(id=ronda_id).first()
    if not ronda:
        return None
    carta_mayor_fuerza = max(
        ronda.cartas.values(),
        key=lambda carta: CATALOGO[carta]["fuerza"],
    )
    for color, carta in ronda.cartas.items():
        if carta == carta_mayor_fuerza:
            return color
    return None