from django.utils import timezone

import random

from django.db import transaction

from ..models.mano import Mano
from ..models.ronda import Ronda
from ..services.resumen_mano_service import create_resumen_mano

from ..models.torneo_usuario import TorneoUsuario
from ..models.usuario import Usuario

from ..selectors.torneo_selector import get_participantes_torneo_by_torneo_id, get_partida_torneo_by_partida_id, get_partidas_torneo_by_fase, get_torneo_by_id

from ..models.partida_torneo import PartidaTorneo
from ..models.partida_usuario import PartidaUsuario

from ..models.partida import Partida

from ..selectors.mano_selector import get_jugadores_en_mesa

from ..selectors.partida_selector import get_colores_disponibles, get_jugadores_actuales_de_partida, get_partida_by_id, get_partida_usuario_by_partida_and_color, get_partida_usuario_by_partida_and_usuario

from ..models.catalogo_cartas import CATALOGO


def obtener_primer_jugador_activo(partida):
    """
    Obtiene el primer jugador activo de la disposición actual.
    """
    if not partida or not partida.disposicion_jugadores:
        return None

    for color in partida.disposicion_jugadores:
        partida_usuario = get_partida_usuario_by_partida_and_color(partida.id, color)
        if partida_usuario and not partida_usuario.retirado and not partida_usuario.abandono:
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
        if partida_usuario and not partida_usuario.retirado and not partida_usuario.abandono:
            partida.turno_actual = color_turno_actual
            partida.save(update_fields=["turno_actual"])
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

        if magicas is None and unicas is None:
            if num_aleatorio < 0.7:
                magicas_selec = random.sample(cartas_magicas, 4)
                unicas_selec = []
            elif num_aleatorio < 0.95:
                magicas_selec = random.sample(cartas_magicas, 3)
                unicas_selec = random.sample(cartas_unicas, 1)
            else:
                magicas_selec = random.sample(cartas_magicas, 2)
                unicas_selec = random.sample(cartas_unicas, 2)
        else:
            magicas_selec = random.sample(cartas_magicas, magicas)
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
        key=lambda jugador: jugador["puntos"] if isinstance(jugador, dict) else jugador.puntos,
        reverse=True
    )

    posicion = 1
    i = 0

    while i < len(jugadores_ordenados):
        jugador_actual = jugadores_ordenados[i]
        puntos = jugador_actual["puntos"] if isinstance(jugador_actual, dict) else jugador_actual.puntos

        empatados = [
            jugador for jugador in jugadores_ordenados
            if (jugador["puntos"] if isinstance(jugador, dict) else jugador.puntos) == puntos
        ]

        posiciones[posicion] = empatados

        posicion += len(empatados)
        i += len(empatados)
    return posiciones

@transaction.atomic
def repartir_cartas(actor, partida_id):
    partida = (
        Partida.objects
        .select_for_update()
        .get(id=partida_id)
    )

    jugadores = get_jugadores_en_mesa(
        partida_id,
        partida.disposicion_jugadores
    )

    primer_jugador_activo = obtener_primer_jugador_activo(partida)

    if not primer_jugador_activo:
        raise ValueError("No hay jugadores activos para repartir la mano.")

    partida_usuario = get_partida_usuario_by_partida_and_usuario(
        partida_id,
        actor.id
    )

    if not partida_usuario or partida_usuario.abandono:
        raise PermissionError("No participas en la partida.")

    random.shuffle(partida.baraja)

    vuelta = 1

    while vuelta < 5:
        for jugador in jugadores:
            if len(jugador.cartas) < 4 and not jugador.abandono:
                carta = partida.baraja.pop(0)
                jugador.cartas.append(carta)

        vuelta += 1

    partida.turno_actual = primer_jugador_activo

    for jugador in jugadores:
        jugador.save()

    partida.save()

def aux_generar_disposicion_jugadores(partida_id):
    """
    Genera la disposición inicial de los jugadores en la partida.
    """

    colores_no_usados = get_colores_disponibles(partida_id)
    disposicion = [color for color in PartidaUsuario.ColorJugador.values if color not in colores_no_usados]
    random.shuffle(disposicion)

    return disposicion

def aux_crear_partidas_torneo(torneo, num_partidas, fase, num_jug_fase):

    partidas = []
    for i in range(num_partidas):
            partida = Partida(
                    nombre=f"{torneo.nombre} - {fase} {i + 1}",
                    num_jugadores=num_jug_fase,
                    fecha_creacion=timezone.now(),
                    fecha_inicio=timezone.now(),
                    longitud=torneo.partidas_longitud,
                    cartas_especiales=torneo.partidas_cartas_especiales,
                    tickets=torneo.partidas_tickets,
                    tiempo_max_turno=torneo.partidas_tiempo_max_turno,
            )
            partida.baraja = aux_generar_baraja_inicial(partida.cartas_especiales, partida.num_jugadores)
            # Mano
            mano = Mano(
                partida=partida,
                num=1
            )
            # Ronda
            ronda = Ronda(
                mano=mano,
                num=0
            )
            partida.save()
            mano.save()
            create_resumen_mano(partida.id)
            ronda.save()
            partidas.append(partida)


    return partidas

def aux_crear_relaciones_partidas_torneo(torneo, partidas):

    if len(partidas) == 8:
        fase = PartidaTorneo.FasePartida.OCTAVOS
    elif len(partidas) == 4:
        fase = PartidaTorneo.FasePartida.CUARTOS
    elif len(partidas) == 2:
        fase = PartidaTorneo.FasePartida.SEMIFINAL
    elif len(partidas) == 1:
        fase = PartidaTorneo.FasePartida.FINAL
    else:
        raise ValueError("Número de partidas no válido para un bracket")

    partidas_por_lado = len(partidas) // 2

    for i, partida in enumerate(partidas):

        lado = i // partidas_por_lado
        pareja = (i % partidas_por_lado) // 2

        partida.save()

        PartidaTorneo.objects.create(
            torneo=torneo,
            partida=partida,
            fase=fase,
            lado=lado,
            pareja=pareja,
            posiciones_finales={}
        )

def aux_asignar_jugadores_a_partidas(participantes, num_partidas, num_jugadores_por_partida, partidas):

    comprobacion = len(participantes) == num_partidas * num_jugadores_por_partida
    if not comprobacion:
        raise ValueError("El número de participantes no coincide con el número de partidas y jugadores por partida")

    participantes = participantes.copy()
    random.shuffle(participantes)

    colores = [
        PartidaUsuario.ColorJugador.ROJO,
        PartidaUsuario.ColorJugador.AZUL,
        PartidaUsuario.ColorJugador.VERDE,
        PartidaUsuario.ColorJugador.AMARILLO,
        PartidaUsuario.ColorJugador.MORADO,
        PartidaUsuario.ColorJugador.NARANJA,
    ]

    for i in range(num_partidas):

        jugadores = participantes[
            i * num_jugadores_por_partida:
            (i + 1) * num_jugadores_por_partida
        ]

        colores_partida = colores[:num_jugadores_por_partida]
        random.shuffle(colores_partida)

        for jugador, color in zip(jugadores, colores_partida):
            PartidaUsuario.objects.create(
                partida=partidas[i],
                usuario_id=jugador["id"],
                color=color,
            )

    # Repartir cartas en cada partida
    for partida in partidas:
        partida.disposicion_jugadores = aux_generar_disposicion_jugadores(partida.id)
        partida.save(update_fields=["disposicion_jugadores"])
        # Asignar repartidor cualquiera de entre los jugadores de la partida
        repartidor = random.choice(partida.disposicion_jugadores)
        actor_cualquiera = get_partida_usuario_by_partida_and_color(partida.id, repartidor)
        repartir_cartas(actor_cualquiera, partida.id)

def aux_obtener_clasificados(posiciones_partida_1, posiciones_partida_2, num_clasificados, desempate_mayor_punt):
    posiciones_globales = {}

    posiciones_globales.update(posiciones_partida_1)
    posiciones_globales.update(posiciones_partida_2)

    posiciones_ordenadas = sorted(
        posiciones_globales.items(),
        key=lambda x: x[1],
        reverse=True
    )

    clasificados = []
    i = 0

    while i < len(posiciones_ordenadas) and len(clasificados) < num_clasificados:

        puntuacion_actual = posiciones_ordenadas[i][1]

        empatados = []

        while (
            i < len(posiciones_ordenadas)
            and posiciones_ordenadas[i][1] == puntuacion_actual
        ):
            empatados.append(posiciones_ordenadas[i][0])
            i += 1

        plazas_restantes = num_clasificados - len(clasificados)

        # Todos los empatados caben: clasifican todos
        if len(empatados) <= plazas_restantes:
            clasificados.extend(empatados)

        # No todos los empatados caben: hay que desempatar
        else:
            if desempate_mayor_punt:
                usuarios = Usuario.objects.filter(id__in=empatados)

                usuarios_ordenados = sorted(
                    usuarios,
                    key=lambda usuario: usuario.puntuacion,
                    reverse=True
                )

                clasificados.extend(
                    usuario.id
                    for usuario in usuarios_ordenados[:plazas_restantes]
                )

            else:
                clasificados.extend(
                    random.sample(empatados, plazas_restantes)
                )

    return clasificados

def aux_asignar_clasificados_a_partidas(partidas, clasificados):
    colores = list(PartidaUsuario.ColorJugador.values)

    for partida, jugadores in zip(partidas, clasificados):

        colores_partida = colores[:len(jugadores)]
        random.shuffle(colores_partida)

        for usuario_id, color in zip(jugadores, colores_partida):
            PartidaUsuario.objects.create(
                partida=partida,
                usuario_id=usuario_id,
                color=color
            )

def aux_eliminar_jugadores_no_clasificados(clasificados):
    clasificados_flat = [usuario_id for sublist in clasificados for usuario_id in sublist]

    participantes_no_clasificados = TorneoUsuario.objects.exclude(usuario_id__in=clasificados_flat)

    for participante in participantes_no_clasificados:
        participante.eliminado = True
        participante.save(update_fields=["eliminado"])

def aux_iniciar_fase_octavos(torneo_id):

    torneo = get_torneo_by_id(torneo_id)
    participantes = get_participantes_torneo_by_torneo_id(torneo_id)

    # Crear las partidas de octavos de final
    partidas = aux_crear_partidas_torneo(torneo, 8, "Octavos de final", torneo.num_jug_oct)

    # Crear relaciones entre el torneo y las partidas
    aux_crear_relaciones_partidas_torneo(torneo, partidas)

    # Asignar jugadores a las partidas de octavos de final
    aux_asignar_jugadores_a_partidas(participantes, 8, torneo.num_jug_oct, partidas)
    
def aux_iniciar_fase_cuartos(torneo_id, inicio=False):

    torneo = get_torneo_by_id(torneo_id)
    participantes = get_participantes_torneo_by_torneo_id(torneo_id)

    # Crear las partidas de cuartos de final
    partidas = aux_crear_partidas_torneo(torneo, 4, "Cuartos de final", torneo.num_jug_cua)

    # Crear relaciones entre el torneo y las partidas
    aux_crear_relaciones_partidas_torneo(torneo, partidas)

    # Asignar jugadores a las partidas de cuartos de final
    if inicio:
        aux_asignar_jugadores_a_partidas(participantes, 4, torneo.num_jug_cua, partidas)
    else:
        partidas_torneo_fase_anterior = get_partidas_torneo_by_fase(torneo_id, PartidaTorneo.FasePartida.OCTAVOS)

        clasificados = []

        for i in range(0, len(partidas_torneo_fase_anterior), 2):
            clasificados.append(
                aux_obtener_clasificados(
                    partidas_torneo_fase_anterior[i].posiciones_finales,
                    partidas_torneo_fase_anterior[i + 1].posiciones_finales,
                    torneo.num_jug_cua,
                    torneo.desempate_mayor_punt
                )
            )

        aux_eliminar_jugadores_no_clasificados(clasificados)

        aux_asignar_clasificados_a_partidas(
            partidas,
            clasificados
        )

def aux_iniciar_fase_semifinales(torneo_id, inicio=False):

    torneo = get_torneo_by_id(torneo_id)
    participantes = get_participantes_torneo_by_torneo_id(torneo_id)

    # Crear las partidas de semifinales
    partidas = aux_crear_partidas_torneo(torneo, 2, "Semifinales", torneo.num_jug_sem)

    # Crear relaciones entre el torneo y las partidas
    aux_crear_relaciones_partidas_torneo(torneo, partidas)

    # Asignar jugadores a las partidas de semifinales
    if inicio:
        aux_asignar_jugadores_a_partidas(participantes, 2, torneo.num_jug_sem, partidas)
    else:
        partidas_torneo_fase_anterior = get_partidas_torneo_by_fase(torneo_id, PartidaTorneo.FasePartida.CUARTOS)
        
        clasificados = []

        for i in range(0, len(partidas_torneo_fase_anterior), 2):
            clasificados.append(
                aux_obtener_clasificados(
                    partidas_torneo_fase_anterior[i].posiciones_finales,
                    partidas_torneo_fase_anterior[i + 1].posiciones_finales,
                    torneo.num_jug_sem,
                    torneo.desempate_mayor_punt
                )
            )

        aux_eliminar_jugadores_no_clasificados(clasificados)

        aux_asignar_clasificados_a_partidas(
            partidas,
            clasificados
        )

def aux_iniciar_fase_final(torneo_id):

    torneo = get_torneo_by_id(torneo_id)

    partida = Partida(
            nombre=f"{torneo.nombre} - Final",
            num_jugadores=torneo.num_jug_fin,
            fecha_creacion=timezone.now(),
            fecha_inicio=timezone.now(),
            longitud=torneo.partidas_longitud,
            cartas_especiales=torneo.partidas_cartas_especiales,
            tickets=torneo.partidas_tickets,
            tiempo_max_turno=torneo.partidas_tiempo_max_turno,
        )

    partida.save()

    partida_torneo = PartidaTorneo(
        partida = partida,
        torneo = torneo,
        fase = PartidaTorneo.FasePartida.FINAL,
        lado = 0,
        pareja = 0,
        posiciones_finales = {}
    )

    partida_torneo.save()

    partidas_torneo_fase_anterior = get_partidas_torneo_by_fase(torneo_id, PartidaTorneo.FasePartida.SEMIFINAL)
            
    clasificados = []

    for i in range(0, len(partidas_torneo_fase_anterior), 2):
        clasificados.append(
            aux_obtener_clasificados(
                partidas_torneo_fase_anterior[i].posiciones_finales,
                partidas_torneo_fase_anterior[i + 1].posiciones_finales,
                torneo.num_jug_sem,
                torneo.desempate_mayor_punt
            )
        )

    aux_eliminar_jugadores_no_clasificados(clasificados)

    aux_asignar_clasificados_a_partidas([partida], clasificados)

def aux_finalizar_torneo(torneo_id):
    torneo = get_torneo_by_id(torneo_id)
    torneo.fecha_fin = timezone.now()
    

def aux_almacenar_posiciones_finales_partida_torneo(partida_id):

    partida_torneo = get_partida_torneo_by_partida_id(partida_id)

    posiciones = {}
    pus_participantes = get_jugadores_actuales_de_partida(partida_id)
    for participante in pus_participantes:
        posiciones[participante["id"]] = participante["puntos"]

    partida_torneo.posiciones_finales = posiciones
    partida_torneo.save(update_fields=["posiciones_finales"])

    pts_fase = get_partidas_torneo_by_fase(partida_torneo.torneo.id, partida_torneo.fase)
    for pt in pts_fase:
        if pt.partida.fecha_fin is None:
            return

    if partida_torneo.fase == PartidaTorneo.FasePartida.OCTAVOS:
        aux_iniciar_fase_cuartos(partida_torneo.torneo.id)
    elif partida_torneo.fase == PartidaTorneo.FasePartida.CUARTOS:
        aux_iniciar_fase_semifinales(partida_torneo.torneo.id)
    elif partida_torneo.fase == PartidaTorneo.FasePartida.SEMIFINAL:
        aux_iniciar_fase_final(partida_torneo.torneo.id)
    else:
        aux_finalizar_torneo(partida_torneo.torneo.id)
