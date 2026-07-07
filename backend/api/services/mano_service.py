from ..selectors.partida_selector import get_partida_by_id, get_partida_usuario_by_partida_and_usuario
from ..selectors.mano_selector import get_jugadores_en_mesa

def repartir_cartas(actor, partida_id):
    """
    Reparte cartas a los jugadores de una partida.
    """
    partida_usuario = get_partida_usuario_by_partida_and_usuario(partida_id, actor.id)
    partida = get_partida_by_id(partida_id).first()
    jugadores = get_jugadores_en_mesa(partida_id, partida.disposicion_jugadores)

    if not partida_usuario:
        raise PermissionError("No participas en la partida.")
    if partida.disposicion_jugadores[-1] != partida_usuario.color:
        raise PermissionError("No eres el repartidor de cartas en esta mano.")
    
    vuelta = 1
    while vuelta < 5:
        for jugador in jugadores:
            if len(jugador.cartas) < 5:
                carta = partida.baraja.pop(0)  # Saca la primera carta de la baraja
                jugador.cartas.append(carta)  # Añade la carta a las cartas del jugador
            else:
                pass
        vuelta += 1
    
    # Guardar cambios
    for jugador in jugadores:
        jugador.save() 
    partida.save() 




    

    