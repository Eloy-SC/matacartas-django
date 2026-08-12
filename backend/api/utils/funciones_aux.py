import random

from ..selectors.partida_selector import get_partida_usuario_by_partida_and_color

from ..models.catalogo_cartas import CATALOGO


def obtener_primer_jugador_activo(partida):
    """
    Obtiene el primer jugador activo de la disposición actual.
    """
    if not partida or not partida.disposicion_jugadores:
        return None

    for color in partida.disposicion_jugadores:
        partida_usuario = get_partida_usuario_by_partida_and_color(partida.id, color)
        if partida_usuario and not partida_usuario.retirado:
            return color

    return None


def aux_siguiente_turno(partida):
    """
    Cambia el turno al siguiente jugador en la disposición de jugadores.
    """
    if not partida.turno_actual:
        raise ValueError("No hay un turno actual definido.")
    
    disposicion = partida.disposicion_jugadores
    indice_actual = disposicion.index(partida.turno_actual)
    for offset in range(1, len(disposicion) + 1):
        indice_siguiente = (indice_actual + offset) % len(disposicion)
        color_turno_actual = disposicion[indice_siguiente]
        partida_usuario = get_partida_usuario_by_partida_and_color(partida.id, color_turno_actual)
        if partida_usuario and not partida_usuario.retirado:
            partida.turno_actual = color_turno_actual
            partida.save()
            return

    raise ValueError("No hay jugadores activos disponibles.")

def aux_generar_baraja_inicial(cartas_especiales, num_jugadores, valiosas=None, magicas=None, unicas=None):
    """
    Genera la baraja inicial de cartas para una partida.
    """

    baraja = [
        nombre
        for nombre, datos in CATALOGO.items()
        if datos["tipo"] == "normal"
    ]

    if cartas_especiales:
        random.seed()  # Inicializa el generador de números aleatorios con una semilla basada en el tiempo actual
        num_aleatorio = random.random()
        cartas_valiosas = [
            nombre
            for nombre, datos in CATALOGO.items()
            if datos["tipo"] == "especial_val"
        ]
        cartas_magicas = [
            nombre
            for nombre, datos in CATALOGO.items()
            if datos["tipo"] == "especial_mag"
        ]
        if num_jugadores == 2 and "MONEDERO_PECULIAR" in cartas_magicas:
            cartas_magicas.remove("MONEDERO_PECULIAR")
        if num_jugadores == 2 and "AS_EXTRANJERO" in cartas_magicas:
            cartas_magicas.remove("AS_EXTRANJERO")
        if num_jugadores == 2 and "CORRUPTOR" in cartas_magicas:
            cartas_magicas.remove("CORRUPTOR")
        if num_jugadores == 2 and "SAQUEADOR_TUMBAS" in cartas_magicas:
            cartas_magicas.remove("SAQUEADOR_TUMBAS")
        cartas_unicas = [
            nombre
            for nombre, datos in CATALOGO.items()
            if datos["tipo"] == "especial_uni"
        ]

        if valiosas is None:
            valiosas_selec = random.sample(cartas_valiosas, 8)
        else:
            valiosas_selec = random.sample(cartas_valiosas, valiosas)

        if magicas is None:
            if num_aleatorio < 0.7:
                magicas_selec = random.sample(cartas_magicas, 4)
            elif num_aleatorio < 0.95:
                magicas_selec = random.sample(cartas_magicas, 3)
            else:
                magicas_selec = random.sample(cartas_magicas, 2)
        else:
            magicas_selec = random.sample(cartas_magicas, magicas)

        if unicas is None:
            if num_aleatorio < 0.7:
                unicas_selec = []
            elif num_aleatorio < 0.95:
                unicas_selec = random.sample(cartas_unicas, 1)
            else:
                unicas_selec = random.sample(cartas_unicas, 2)
        else:
            unicas_selec = random.sample(cartas_unicas, unicas)

        cartas_especiales_selec = valiosas_selec + magicas_selec + unicas_selec
        cartas_especiales_selec_posiciones = {
            CATALOGO[nombre]["posicion"]
            for nombre in cartas_especiales_selec
        }

        baraja = [
            carta
            for carta in baraja
            if CATALOGO[carta]["posicion"] not in cartas_especiales_selec_posiciones
        ]
        baraja.extend(cartas_especiales_selec)

    random.shuffle(baraja)

    return baraja

def aux_fin_partida_mod_puntos(partida_id, jugadores):
    """
    Modifica los puntos de los jugadores al finalizar la partida según las reglas del juego.
    """

    ganadores = []
    max_puntos = 0
    jug_as_extranjero = None
    puntos_ganados_por_kills = {}
    puntos_perdidos_por_deaths = {}

    # Modificación de puntos según acumuladores de kills y deaths
    for j in jugadores:
        jugador = get_partida_usuario_by_partida_and_color(partida_id, j["color"])
        puntos_extra_kills = j.get("acumulador_kills", 0) // 2
        puntos_extra_deaths = j.get("acumulador_deaths", 0) // 4
        jugador.puntos += puntos_extra_kills
        jugador.puntos -= puntos_extra_deaths
        puntos_ganados_por_kills[jugador.color] = puntos_extra_kills
        puntos_perdidos_por_deaths[jugador.color] = puntos_extra_deaths
        jugador.save()

        if jugador.eff_as_extranjero:
            jug_as_extranjero = jugador.color

        if jugador.puntos > max_puntos:
            max_puntos = jugador.puntos
            ganadores = [jugador.color]
        elif jugador.puntos == max_puntos:
            ganadores.append(jugador.color)

    res = {
        "puntos_ganados_por_kills": puntos_ganados_por_kills,
        "puntos_perdidos_por_deaths": puntos_perdidos_por_deaths,
    }
    
    # Efecto del as extranjero
    for j in jugadores:
            if j["color"] == jug_as_extranjero:
                jugador = get_partida_usuario_by_partida_and_color(partida_id, j["color"])
                if jugador.puntos + 15 >= max_puntos:
                    diff = max_puntos - jugador.puntos
                    res["jug_as_extranjero"] = jug_as_extranjero
                    res["puntuacion_extra_jug_as_extranjero"] = diff + 1
                    jugador.puntos += diff + 1
                    jugador.save()
                break

    return res

    

def aux_fin_partida_posiciones(jugadores):
    """
    Modifica los puntos de los jugadores al finalizar la partida según las posiciones finales.
    """

    # Determinar las posiciones definitivas con efectos y puntos def. calculados
    posiciones = {1: [], 2: [], 3: [], 4: [], 5: [], 6: []}

    jugadores_ordenados = sorted(
        jugadores,
        key=lambda jugador: jugador.puntos,
        reverse=True
    )

    posicion = 1
    i = 0

    while i < len(jugadores_ordenados):
        puntos = jugadores_ordenados[i].puntos

        empatados = [
            jugador for jugador in jugadores_ordenados
            if jugador.puntos == puntos
        ]

        posiciones[posicion] = empatados

        posicion += len(empatados)
        i += len(empatados)
    return posiciones