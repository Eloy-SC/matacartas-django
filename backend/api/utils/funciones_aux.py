

def aux_siguiente_turno(partida):
    """
    Cambia el turno al siguiente jugador en la disposición de jugadores.
    """
    if not partida.turno_actual:
        raise ValueError("No hay un turno actual definido.")
    
    disposicion = partida.disposicion_jugadores
    indice_actual = disposicion.index(partida.turno_actual)
    indice_siguiente = (indice_actual + 1) % len(disposicion)
    partida.turno_actual = disposicion[indice_siguiente]
    partida.save()