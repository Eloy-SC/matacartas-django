import random

from ..services.partida_service import aux_generar_baraja_inicial

from ..models.catalogo_tickets import TICKETS, PROBABILIDAD_TICKET, PROBABILIDAD_TICKET_CLASE, PROBABILIDAD_TICKET_CLASE_ULTIMO

from ..selectors.mano_selector import get_tickets_clase_0, get_tickets_clase_1, get_tickets_clase_2, get_tickets_clase_3

from ..selectors.partida_selector import get_colores_jugadores, get_colores_ordenados_por_puntuacion, get_colores_ordenados_por_puntuacion_con_ticket, get_jugadores_actuales_de_partida, get_partida_by_id, get_partida_by_id, get_partida_usuario_by_partida_and_color, get_partida_usuario_by_partida_and_usuario


def repartir_tickets(partida_id):
    partida_num_jug = get_partida_by_id(partida_id).num_jugadores
    partida_especiales = get_partida_by_id(partida_id).cartas_especiales
    jugadores = get_colores_ordenados_por_puntuacion(partida_id)
    puntuaciones = list(jugadores.keys())

    tickets_por_clase = {
        0: get_tickets_clase_0(),
        1: get_tickets_clase_1(),
        2: get_tickets_clase_2(),
        3: get_tickets_clase_3(),
    }

    for indice, puntuacion in enumerate(puntuaciones):
        posicion = indice + 1

        # El primero nunca recibe
        if posicion == 1:
            continue

        # Probabilidades correspondientes a la posición
        if posicion == len(puntuaciones):
            probabilidad_ticket = 1.0
            probabilidades_clase = PROBABILIDAD_TICKET_CLASE_ULTIMO
        else:
            probabilidad_ticket = PROBABILIDAD_TICKET[posicion]
            probabilidades_clase = PROBABILIDAD_TICKET_CLASE[posicion]

        # Cada jugador recibe o no un ticket, aunque estén empatados (por eso el for)
        for color in jugadores[puntuacion]:

            if random.random() >= probabilidad_ticket:
                continue

            clase = random.choices(
                list(probabilidades_clase.keys()),
                weights=list(probabilidades_clase.values()),
                k=1
            )[0]

            ticket = random.choice(tickets_por_clase[clase])
            # Si el ticket es de retirada obligada y hay 2 jugadores, se vuelve a elegir hasta que no lo sea
            if TICKETS[ticket]["seccion"] == "retirada_obligada" and partida_num_jug == 2:
                while TICKETS[ticket]["seccion"] == "retirada_obligada":
                    ticket = random.choice(tickets_por_clase[clase])
            # Si el ticket es de cambio de baraja y no hay cartas especiales, se vuelve a elegir hasta que no lo sea
            elif TICKETS[ticket]["seccion"] == "cambio_baraja" and not partida_especiales:
                while TICKETS[ticket]["seccion"] == "cambio_baraja":
                    ticket = random.choice(tickets_por_clase[clase])

            partida_usuario = get_partida_usuario_by_partida_and_color(partida_id, color)
            if partida_usuario:
                partida_usuario.ticket = ticket
                partida_usuario.save()

def usar_ticket(actor, partida_id, ticket):
    """
    Permite a un jugador usar un ticket en la partida.
    """
    partida_usuario = get_partida_usuario_by_partida_and_usuario(partida_id, actor.id)
    if not partida_usuario:
        raise PermissionError("No participas en la partida.")

    if partida_usuario.ticket != ticket:
        raise ValueError("No tienes este ticket.")
    
    partida = get_partida_by_id(partida_id)
    if not partida.tickets:
        raise PermissionError("No se pueden usar tickets en esta partida.")
    if partida.turno_actual != partida_usuario.color:
        raise PermissionError("No es tu turno para usar un ticket.")

    if ticket.startswith("ticket_cb"):
        aux_usar_ticket_cb(partida_id, ticket)
    elif ticket.startswith("ticket_ic"):
        aux_usar_ticket_ic(partida_id, ticket, partida_usuario.color)
    elif ticket.startswith("ticket_pp"):
        aux_usar_ticket_pp(partida_id, ticket, partida_usuario.color)
    elif ticket.startswith("ticket_rp"):
        aux_usar_ticket_rp(partida_id, ticket, partida_usuario.color)
    elif ticket.startswith("ticket_cp"):
        aux_usar_ticket_cp(partida_id, ticket, partida_usuario.color)
    elif ticket.startswith("ticket_ro"):
        aux_usar_ticket_ro(partida_id, ticket, partida_usuario.color)
    elif ticket.startswith("ticket_rt"):
        aux_usar_ticket_rt(partida_id, ticket, partida_usuario.color)
    else:
        raise ValueError("Ticket no reconocido.")

    # Después de usar el ticket, se elimina del jugador.
    partida_usuario.ticket = None
    partida_usuario.save()

def aux_usar_ticket_cb(partida_id, ticket):
    partida = get_partida_by_id(partida_id)
    baraja_nueva = None
    random.seed()
    num_aleatorio = random.random()

    if ticket.endswith("aleatorio"):
        baraja_nueva = aux_generar_baraja_inicial(partida.cartas_especiales, partida.num_jugadores)
    elif ticket.endswith("con_unicas"):
        if num_aleatorio < 0.7:
            baraja_nueva = aux_generar_baraja_inicial(partida.cartas_especiales, partida.num_jugadores, valiosas=8, magicas=3, unicas=1)
        else:
            baraja_nueva = aux_generar_baraja_inicial(partida.cartas_especiales, partida.num_jugadores, valiosas=8, magicas=2, unicas=2)
    elif ticket.endswith("valiosa"):
        baraja_nueva = aux_generar_baraja_inicial(partida.cartas_especiales, partida.num_jugadores, valiosas=12, magicas=0, unicas=0)
    elif ticket.endswith("magica"):
        baraja_nueva = aux_generar_baraja_inicial(partida.cartas_especiales, partida.num_jugadores, valiosas=8, magicas=6, unicas=0)
    elif ticket.endswith("unica"):
        baraja_nueva = aux_generar_baraja_inicial(partida.cartas_especiales, partida.num_jugadores, valiosas=8, magicas=4, unicas=2)
    elif ticket.endswith("todas"):
        baraja_nueva = aux_generar_baraja_inicial(partida.cartas_especiales, partida.num_jugadores, valiosas=38, magicas=8, unicas=2)
    else:
        raise ValueError("Ticket no reconocido.")

    partida.baraja = baraja_nueva
    partida.save()

def aux_usar_ticket_ic(partida_id, ticket, actor_color):
    dic_colores = get_colores_ordenados_por_puntuacion(partida_id)
    dic_colores.remove(actor_color)

    if ticket.endswith("azar"):
        puntuacion = random.choice(dic_colores)
        color_objetivo = random.choice(list(dic_colores[puntuacion].values()))
    elif ticket.endswith("primero"):
        color_objetivo = random.choice(list(dic_colores[dic_colores[0]].values()))  # El primero de la lista es el que tiene más puntos
    else:
        raise ValueError("Ticket no reconocido.")

    actor = get_partida_usuario_by_partida_and_color(partida_id, actor_color)
    comodin_actor = actor.carta_comodin
    objetivo = get_partida_usuario_by_partida_and_color(partida_id, color_objetivo)
    comodin_objetivo = objetivo.carta_comodin
    intercambio = comodin_actor # variable de intercambio para almacenar el comodin del actor temporalmente
    comodin_actor = comodin_objetivo
    comodin_objetivo = intercambio

    actor.save()
    objetivo.save()

def aux_usar_ticket_pp(partida_id, ticket, actor_color):
    dic_colores = get_colores_ordenados_por_puntuacion(partida_id)
    dic_colores.remove(actor_color)

    if ticket.contains("2"):
        puntos = 2
    elif ticket.contains("4"):
        puntos = 4
    elif ticket.contains("6"):
        puntos = 6
    else:
        raise ValueError("Ticket no reconocido.")

    if ticket.endswith("todos"):
        colores_objetivo = []
        for puntuacion in dic_colores:
            for color in dic_colores[puntuacion]:
                colores_objetivo.append(color)
        for color in get_colores_jugadores(partida_id):
            if color in colores_objetivo:
                jugador = get_partida_usuario_by_partida_and_color(partida_id, color)
                jugador.puntos -= puntos
                jugador.save()
    else:
        if ticket.endswith("azar"):
            puntuacion = random.choice(dic_colores)
            color_objetivo = random.choice(list(dic_colores[puntuacion].values()))
        elif ticket.endswith("primero"):
            color_objetivo = random.choice(list(dic_colores[dic_colores[0]].values()))  # El primero de la lista es el que tiene más puntos
        else:
            raise ValueError("Ticket no reconocido.")
        objetivo = get_partida_usuario_by_partida_and_color(partida_id, color_objetivo)
        objetivo.puntos -= puntos
        objetivo.save()

def aux_usar_ticket_rp(partida_id, ticket, actor_color):

    aux_usar_ticket_pp(partida_id, ticket, actor_color)
    jugador_actor = get_partida_usuario_by_partida_and_color(partida_id, actor_color)
    jugador_actor.puntos += 2
    jugador_actor.save()

def aux_usar_ticket_cp(partida_id, ticket, actor_color):
    jugador_actor = get_partida_usuario_by_partida_and_color(partida_id, actor_color)

    if ticket.endswith("2"):
        jugador_actor.puntos += 2
    elif ticket.endswith("4"):
        jugador_actor.puntos += 4
    elif ticket.endswith("6"):
        jugador_actor.puntos += 6
    elif ticket.endswith("10"):
        jugador_actor.puntos += 10
    else:
        raise ValueError("Ticket no reconocido.")

    jugador_actor.save()

def aux_usar_ticket_ro(partida_id, ticket, actor_color):
    dic_colores = get_colores_ordenados_por_puntuacion(partida_id)
    dic_colores.remove(actor_color)

    if ticket.endswith("azar"):
        puntuacion = random.choice(dic_colores)
        color_objetivo = random.choice(list(dic_colores[puntuacion].values()))
    elif ticket.endswith("primero"):
        color_objetivo = random.choice(list(dic_colores[dic_colores[0]].values()))  # El primero de la lista es el que tiene más puntos
    else:
        raise ValueError("Ticket no reconocido.")

    objetivo = get_partida_usuario_by_partida_and_color(partida_id, color_objetivo)
    objetivo.retirado = True
    objetivo.save()

def aux_usar_ticket_rt(partida_id, ticket, actor_color):
    dic_colores = get_colores_ordenados_por_puntuacion_con_ticket(partida_id)
    dic_colores.remove(actor_color)
    if dic_colores is None or len(dic_colores) == 0:
        raise ValueError("No hay jugadores con tickets para robar.")

    if ticket.endswith("azar"):
        puntuacion = random.choice(dic_colores)
        color_objetivo = random.choice(list(dic_colores[puntuacion].values()))
    elif ticket.endswith("primero"):
        color_objetivo = random.choice(list(dic_colores[dic_colores[0]].values()))  # El primero de la lista es el que tiene más puntos
    elif ticket.endswith("mayor_clase"):
        color_objetivo = None
        for puntuacion in dic_colores:
            for color in dic_colores[puntuacion]:
                if color_objetivo is None or \
                    TICKETS[get_partida_usuario_by_partida_and_color(partida_id, color).ticket]["clase"] \
                        < TICKETS[get_partida_usuario_by_partida_and_color(partida_id, color_objetivo).ticket]["clase"]:
                    color_objetivo = color
    else:
        raise ValueError("Ticket no reconocido.")

    actor = get_partida_usuario_by_partida_and_color(partida_id, actor_color)
    objetivo = get_partida_usuario_by_partida_and_color(partida_id, color_objetivo)
    actor.ticket = objetivo.ticket
    actor.save()
    objetivo.ticket = None
    objetivo.save()