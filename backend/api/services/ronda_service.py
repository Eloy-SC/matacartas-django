from ..selectors.ronda_selector import get_rondas_de_mano

from ..utils.funciones_aux import aux_siguiente_turno

from ..selectors.mano_selector import get_mano_actual

from ..selectors.partida_selector import get_partida_by_id, get_partida_usuario_by_partida_and_usuario


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
        ganador_ronda()  # Determinar ganador de la ronda y preparar la siguiente

def ganador_ronda():
    pass