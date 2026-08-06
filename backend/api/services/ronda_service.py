from ..models.catalogo_cartas import CATALOGO

from ..models.ronda import Ronda

from ..selectors.ronda_selector import get_cartas_lanzadas_en_mano, get_cartas_lanzadas_en_mano_hasta_ronda, get_cartas_lanzadas_en_mano_por_jugador, get_jugador_lanzador_carta_mayor_fuerza, get_rondas_de_mano

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

    mano_actualizada = get_mano_actual(partida_id)
    if mano_actualizada and mano_actualizada.ganador is not None:
        return True  # Indica que la mano ha terminado
    else:
        return False  # Indica que la mano sigue en curso

def ganador_ronda(partida_id):

    ronda_actual = get_rondas_de_mano(get_mano_actual(partida_id).id)[-1]
    cartas_jugadas = ronda_actual.cartas
    especiales = False
    for carta in cartas_jugadas.values():
        if CATALOGO[carta]["tipo"].startswith("especial"):
            especiales = True
            break
    if especiales:
        aux_asignar_puntos_inmediatos_por_cartas_especiales(partida_id)
    else:
        carta_mayor_fuerza = aux_get_carta_mayor_fuerza(partida_id)
        cartas_matadoras = aux_get_cartas_matadoras(carta_mayor_fuerza)
        cartas_matadoras_jugadas = [carta for carta in cartas_jugadas.values() if carta in cartas_matadoras]

        if cartas_matadoras_jugadas:
            carta_ganadora = max(
                cartas_matadoras_jugadas,
                key=lambda carta: CATALOGO[carta]["fuerza"],
            )
            ganador = [color for color, carta in cartas_jugadas.items() if carta == carta_ganadora][0]
        else:
            ganador = [color for color, carta in cartas_jugadas.items() if carta == carta_mayor_fuerza][0]

    jugador_ganador = get_partida_usuario_by_partida_and_color(partida_id, ganador)
    carta_ganadora = cartas_jugadas[ganador]
    if carta_ganadora in aux_get_cartas_matadoras(carta_mayor_fuerza):
        if especiales == False:
            jugador_ganador.puntos += CATALOGO[carta_mayor_fuerza]["recompensa"]
        else: 
            # SAQUEADOR DE TUMBAS
            for carta in cartas_jugadas.values():
                if carta == "SAQUEADOR_TUMBAS":
                    lanzador_saqueador_tumbas = next(
                            (jugador for jugador, carta in cartas_jugadas.items()
                            if carta == "SAQUEADOR_TUMBAS"),
                            None
                    )
                    jugador_saqueador_tumbas = get_partida_usuario_by_partida_and_color(partida_id, lanzador_saqueador_tumbas)
                    jugador_saqueador_tumbas.puntos += 3
                    jugador_saqueador_tumbas.puntos += CATALOGO[carta_mayor_fuerza]["recompensa"]
        jugador_ganador.acumulador_kills += 1
        jugador_ganador.save()
        color_jug_perdedor = get_jugador_lanzador_carta_mayor_fuerza(ronda_actual.id)
        jugador_perdedor = get_partida_usuario_by_partida_and_color(partida_id, color_jug_perdedor)
        jugador_perdedor.acumulador_deaths += 1
        jugador_perdedor.save()

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

def aux_get_cartas_matadoras(carta):

    matadoras = CATALOGO[carta].get("matadoras", ())
    return tuple(matadoras)

def aux_resolver_ganador_mano(partida_id):
    mano_actual = get_mano_actual(partida_id)
    rondas = get_rondas_de_mano(mano_actual.id)
    especiales = False
    for carta in get_cartas_lanzadas_en_mano(mano_actual.id):
        if CATALOGO[carta]["tipo"].startswith("especial"):
            especiales = True
            break

    ganadores = {}
    for ronda in rondas:
        if ronda.num < 1 or ronda.num > 3 or ronda.ganador is None:
            continue
        ganadores[ronda.ganador] = ganadores.get(ronda.ganador, 0) + 1

    if not ganadores:
        raise ValueError("No hay ganador válido para resolver la mano.")

    max_victorias = max(ganadores.values())
    colores_con_maximo = [color for color, victorias in ganadores.items() if victorias == max_victorias]

    # Si alguien ganó 2 o 3 rondas, gana la mano sin desempate por comodines.
    if max_victorias >= 2:
        ganador_mano = colores_con_maximo[0]
    # Solo hay desempate cuando las tres rondas tienen tres ganadores distintos (1-1-1).
    elif len(colores_con_maximo) == 3: 
        # Si hay desempate, aqui no se asignan puntos extra, eso se hace en la propia función de desempate
        ganador_mano = aux_resolver_desempate_comodines(partida_id, colores_con_maximo, especiales)
    else:
        if especiales:
            aux_asignar_puntos_extra_final_mano(partida_id)
        ganador_mano = colores_con_maximo[0]

    ganador_usuario = get_partida_usuario_by_partida_and_color(partida_id, ganador_mano)
    ganador_usuario.puntos += 4
    ganador_usuario.save()
    aux_asignar_puntos_extra_ganador_mano(partida_id, ganador_mano)

    mano_actual.ganador = ganador_mano
    mano_actual.save()

def aux_resolver_desempate_comodines(partida_id, ganadores, especiales):

    ronda_comodines = Ronda(mano=get_mano_actual(partida_id), num=4, cartas={}, cambios=2)
    jugadores = get_jugadores_actuales_de_partida(partida_id)
    for jugador in jugadores:
        if jugador["color"] in ganadores:
            ronda_comodines.cartas[jugador["color"]] = jugador["carta_comodin"]
    ronda_comodines.save()
    comodines_a_usar = {
        (nombre, CATALOGO[nombre]["riqueza"])
        for nombre in ronda_comodines.cartas.values()
    }
    carta_mayor_riqueza = max(comodines_a_usar, key=lambda x: x[1])
    ganador = [color for color, carta in ronda_comodines.cartas.items() if carta == carta_mayor_riqueza[0]][0]

    if especiales:
        # Asignar puntos extra habiendose definido la ronda de comodines
        aux_asignar_puntos_extra_final_mano(partida_id)

        # Asignar efecto de As Extranjero si el ganador de la ronda de comodines jugó el As Extranjero
        for color in ganadores:
            if color == ganador and carta_mayor_riqueza[0] == "AS_EXTRANJERO":
                jugador_ganador = get_partida_usuario_by_partida_and_color(partida_id, color)
                jugador_ganador.eff_as_extranjero == True
                jugador_ganador.save()
                for jugador in jugadores:
                    if jugador["eff_as_extranjero"] and jugador["color"] != color:
                        jugador_perdedor = get_partida_usuario_by_partida_and_color(partida_id, jugador["color"])
                        jugador_perdedor.eff_as_extranjero == False
                        jugador_perdedor.save()

    return ganador

def aux_asignar_puntos_inmediatos_por_cartas_especiales(partida_id):
    ronda_actual = get_rondas_de_mano(get_mano_actual(partida_id).id)[-1]
    cartas_jugadas = ronda_actual.cartas

    # VINOS VIEJOS
    lanzadores_vinos_viejos = [color for color, carta in cartas_jugadas.items() if carta.endswith("_VINOS_VIEJOS")]
    if lanzadores_vinos_viejos:
        for carta in cartas_jugadas.values():
            if carta.endswith("_COPAS"):
                for color in lanzadores_vinos_viejos:
                    jugador = get_partida_usuario_by_partida_and_color(partida_id, color)
                    jugador.puntos += 2
                    jugador.save()
                break

def aux_asignar_puntos_extra_ganador_mano(partida_id, ganador_mano):
    jugador = get_partida_usuario_by_partida_and_color(partida_id, ganador_mano)
    mano_actual = get_mano_actual(partida_id)

    # JOYAS REALES
    cartas_lanzadas_por_jugador = get_cartas_lanzadas_en_mano_por_jugador(mano_actual.id, ganador_mano)
    cartas_joyas = []
    for carta in cartas_lanzadas_por_jugador:
        if carta.endswith("_JOYAS_REALES"):
            cartas_joyas.append(carta)
    if len(cartas_joyas) > 1:
        jugador.puntos += 3
    elif len(cartas_joyas) > 0:
        jugador.puntos += 2
    jugador.save()

def aux_asignar_puntos_extra_final_mano(partida_id):

    mano_actual = get_mano_actual(partida_id)

    # MERCADER
    for color in mano_actual.disposicion_jugadores:
        cartas_lanzadas_por_jugador = get_cartas_lanzadas_en_mano_por_jugador(mano_actual.id, color)
        if any(carta.endswith("_MERCADER") for carta in cartas_lanzadas_por_jugador):
            ronda_mercader_lanzado = cartas_lanzadas_por_jugador.index(next(carta for carta in cartas_lanzadas_por_jugador if carta.endswith("_MERCADER"))) + 1
            cartas_mercancias = []
            cartas_lanzadas_mano_hasta_ronda = get_cartas_lanzadas_en_mano_hasta_ronda(mano_actual.id, ronda_mercader_lanzado)
            for carta in cartas_lanzadas_mano_hasta_ronda:
                if carta.endswith("_OROS") \
                or carta.endswith("_JOYAS_REALES") \
                or carta.endswith("_COPAS") \
                or carta.endswith("_VINOS_VIEJOS"):
                    cartas_mercancias.append(carta)
            lanzador_de_mercader = get_partida_usuario_by_partida_and_color(partida_id, color)
            if len(cartas_mercancias) >= 1 and len(cartas_mercancias) <= 6:
                lanzador_de_mercader.puntos += cartas_mercancias.count()
                lanzador_de_mercader.save()
            elif len(cartas_mercancias) > 6:
                lanzador_de_mercader.puntos += 6
                lanzador_de_mercader.save()

    # REBELDE
    for color in mano_actual.disposicion_jugadores:
        cartas_lanzadas_por_jugador = get_cartas_lanzadas_en_mano_por_jugador(mano_actual.id, color)
        if any(carta.endswith("_REBELDE") for carta in cartas_lanzadas_por_jugador):
            cartas_bastos = []
            cartas_lanzadas_mano = get_cartas_lanzadas_en_mano(mano_actual.id)
            for carta in cartas_lanzadas_mano:
                if carta.endswith("_BASTOS"):
                    cartas_bastos.append(carta)
                elif carta.endswith("_BASTOS_PUNTIAGUDOS"):
                    cartas_bastos.append(carta)
            lanzador_de_rebelde = get_partida_usuario_by_partida_and_color(partida_id, color)
            if len(cartas_bastos) >= 1 and len(cartas_bastos) <= 8:
                lanzador_de_rebelde.puntos += cartas_bastos.count()
                lanzador_de_rebelde.save()
            elif len(cartas_bastos) > 8:
                lanzador_de_rebelde.puntos += 8
                lanzador_de_rebelde.save()

    # SEGADOR
    for color in mano_actual.disposicion_jugadores:
        cartas_lanzadas_por_jugador = get_cartas_lanzadas_en_mano_por_jugador(mano_actual.id, color)
        if any(carta.endswith("_SEGADOR") for carta in cartas_lanzadas_por_jugador):
            cartas_valiosas_lanzadas = []
            cartas_lanzadas_mano = get_cartas_lanzadas_en_mano(mano_actual.id)
            for carta in cartas_lanzadas_mano:
                tipo = CATALOGO[carta]["tipo"]
                if tipo == "especial_val":
                    cartas_valiosas_lanzadas.append(carta)
            lanzador_de_segador = get_partida_usuario_by_partida_and_color(partida_id, color)
            if len(cartas_valiosas_lanzadas) >= 1 and len(cartas_valiosas_lanzadas) <= 6:
                lanzador_de_segador.puntos += 2*cartas_valiosas_lanzadas.count()
                lanzador_de_segador.save()
            elif len(cartas_valiosas_lanzadas) > 6:
                lanzador_de_segador.puntos += 12
                lanzador_de_segador.save()

    # MONEDERO PECULIAR
    for color in mano_actual.disposicion_jugadores:
        cartas_lanzadas_por_jugador = get_cartas_lanzadas_en_mano_por_jugador(mano_actual.id, color)
        if any(carta.endswith("_MONEDERO_PECULIAR") for carta in cartas_lanzadas_por_jugador):
            lanzador_de_monedero = get_partida_usuario_by_partida_and_color(partida_id, color)
            lanzador_de_monedero.puntos += lanzador_de_monedero.eff_acum_monedero
            lanzador_de_monedero.eff_acum_monedero = 0
            lanzador_de_monedero.save()


def aux_determinar_ganador_ronda_con_especiales(partida_id):
    pass