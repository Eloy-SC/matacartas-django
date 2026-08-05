from backend.api.models.catalogo_cartas import CATALOGO
from backend.api.models.mano import Mano

from ..models.ronda import Ronda

from ..selectors.ronda_selector import get_rondas_de_mano

from ..utils.funciones_aux import aux_siguiente_turno

from ..selectors.mano_selector import get_mano_actual

from ..selectors.partida_selector import get_jugadores_actuales_de_partida, get_partida_by_id, get_partida_usuario_by_partida_and_color, get_partida_usuario_by_partida_and_usuario


def jugar_carta(user, partida_id, carta):
    """
    Lógica para que un jugador juegue una carta en la partida.
    """
    partida = get_partida_by_id(partida_id).first()
    if not partida:
        raise ValueError("Partida no encontrada.")
    
    partida_usuario = get_partida_usuario_by_partida_and_usuario(partida_id, user.id)
    if not partida_usuario:
        raise PermissionError("No participas en la partida.")
    if partida.turno_actual != partida_usuario.color:
        raise PermissionError("No es tu turno para jugar.")
    
    mano = get_mano_actual(partida_id)
    ronda_actual = get_rondas_de_mano(mano.id)[-1]  # Obtener la ult ronda de la mano actual

    if carta not in partida_usuario.cartas:
        raise ValueError("No tienes esa carta en tu mano.")
    if carta in ronda_actual.cartas.values():
        raise ValueError("Esa carta ya ha sido jugada en esta ronda.")
    
    # Registrar la carta jugada
    ronda_actual.cartas[partida_usuario.color] = carta
    ronda_actual.save()

    partida_usuario.cartas.remove(carta)
    partida_usuario.save()

    aux_siguiente_turno(partida)  # Avanzar al siguiente turno
    if partida.turno_actual == partida.disposicion_jugadores[0]:  # Si el turno vuelve al primer jugador, iniciar nueva ronda
        ganador_ronda(partida_id)  # Determinar ganador de la ronda y preparar la siguiente

    if mano.ganador is not None:
        return True  # Indica que la mano ha terminado
    else:
        return False  # Indica que la mano sigue en curso

def ganador_ronda(partida_id):

    ronda_actual = get_rondas_de_mano(get_mano_actual(partida_id).id)[-1]
    cartas_jugadas = ronda_actual.cartas
    especiales = False
    for carta in cartas_jugadas.values():
        if CATALOGO[carta]["tipo"] == "especial":
            especiales = True
            break
    if especiales:
        pass
    else:
        carta_mayor_fuerza = aux_get_carta_mayor_fuerza(partida_id)
        carta_matadora = aux_get_carta_matadora(carta_mayor_fuerza)
        if carta_matadora and carta_matadora in cartas_jugadas.values():
            ganador = [color for color, carta in cartas_jugadas.items() if carta == carta_matadora][0]
        else:
            ganador = [color for color, carta in cartas_jugadas.items() if carta == carta_mayor_fuerza][0]

    jugador_ganador = get_partida_usuario_by_partida_and_color(partida_id, ganador)
    if cartas_jugadas[ganador] == carta_matadora: 
        jugador_ganador.puntos += CATALOGO[carta_mayor_fuerza]["recompensa"]

    ronda_actual.ganador = ganador
    ronda_actual.save()        

    num_ronda = ronda_actual.num
    if num_ronda < 3:
        nueva_ronda = Ronda(mano=get_mano_actual(partida_id), num=num_ronda + 1, cartas={}, cambios=2)
        nueva_ronda.save()
    else:
        aux_resolver_ganador_mano(partida_id)

def aux_get_carta_mayor_fuerza(partida_id):
    ronda_actual = get_rondas_de_mano(get_mano_actual(partida_id).id)[-1]
    cartas_jugadas_fuerza = {
        (nombre, CATALOGO[nombre]["fuerza"])
        for nombre in ronda_actual.cartas.values()
    }
    carta_mayor_fuerza = max(cartas_jugadas_fuerza, key=lambda x: x[1])
    return carta_mayor_fuerza[0]

def aux_get_carta_matadora(carta):

    matadoras = CATALOGO[carta].get("matadoras", [])
    carta_matadora = matadoras[-1] if matadoras else None
    return carta_matadora

def aux_resolver_ganador_mano(partida_id):
    mano_actual = get_mano_actual(partida_id)
    rondas = get_rondas_de_mano(mano_actual.id)
    ganadores = {}
    for ronda in rondas:
        ganadores[ronda.ganador] = ganadores.get(ronda.ganador, 0) + 1
    if len(ganadores) <= 2:
        ganador_mano = max(ganadores, key=ganadores.get)
    else:
        ganador_mano = aux_resolver_desempate_comodines(partida_id, ganadores.keys())

    ganador_usuario = get_partida_usuario_by_partida_and_color(partida_id, ganador_mano)
    ganador_usuario.puntos += 4
    ganador_usuario.save()

    mano_actual.ganador = ganador_mano
    mano_actual.save()

def aux_resolver_desempate_comodines(partida_id, ganadores):

    ronda_comodines = Ronda(mano=get_mano_actual(partida_id), num=4, cartas={}, cambios=2)
    jugadores = get_jugadores_actuales_de_partida(partida_id)
    for jugador in jugadores:
        if jugador["color"] in ganadores:
            ronda_comodines.cartas[jugador["color"]] = jugador["carta_comodin"]
    comodines_a_usar = {
        (nombre, CATALOGO[nombre]["riqueza"])
        for nombre in ronda_comodines.cartas.values()
    }
    carta_mayor_riqueza = max(comodines_a_usar, key=lambda x: x[1])
    ganador = [color for color, carta in ronda_comodines.cartas.items() if carta == carta_mayor_riqueza[0]][0]
    return ganador

def aux_determinar_ganador_ronda_con_especiales(partida_id):
    pass