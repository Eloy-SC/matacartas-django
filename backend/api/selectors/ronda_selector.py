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

def get_cartas_lanzadas_en_mano_por_jugador(mano_id, jugador_color):
    """
    Obtiene las cartas lanzadas en una mano por un jugador específico.
    """

    rondas = get_rondas_de_mano(mano_id)
    cartas_lanzadas = []
    for ronda in rondas:
        if jugador_color in ronda.cartas:
            cartas_lanzadas.append(ronda.cartas[jugador_color])
    return cartas_lanzadas

def get_cartas_lanzadas_en_mano(mano_id):
    """
    Obtiene todas las cartas lanzadas en una mano.
    """
    rondas = get_rondas_de_mano(mano_id)
    cartas_lanzadas = []
    for ronda in rondas:
        cartas_lanzadas.extend(ronda.cartas.values())
    return cartas_lanzadas

def get_cartas_lanzadas_en_mano_hasta_ronda(mano_id, ronda_num):
    """
    Obtiene todas las cartas lanzadas en una mano hasta una ronda específica.
    """
    rondas = get_rondas_de_mano(mano_id)
    cartas_lanzadas = []
    for ronda in rondas:
        if ronda.num > ronda_num:
            break
        cartas_lanzadas.extend(ronda.cartas.values())
    return cartas_lanzadas

def get_cartas_valiosas_utilizadas_en_mano(mano_id):
    """
    Obtiene las cartas valiosas utilizadas en una mano.
    """
    rondas = get_rondas_de_mano(mano_id)
    cartas_valiosas_utilizadas = []
    for ronda in rondas:
        for carta in ronda.cartas.values():
            if CATALOGO[carta]["tipo"] == "especial_val":
                cartas_valiosas_utilizadas.append(carta)
    return cartas_valiosas_utilizadas

def get_carta_equivalente(carta):
    """
    Obtiene la carta equivalente a una carta valiosa.
    """
    for c in CATALOGO:
        if CATALOGO[c]["posicion"] == CATALOGO[carta]["posicion"] and CATALOGO[c]["tipo"] == "normal":
            return c
    return None