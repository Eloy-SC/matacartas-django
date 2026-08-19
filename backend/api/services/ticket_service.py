import random

from ..selectors.mano_selector import get_mano_actual
from ..selectors.ronda_selector import get_rondas_de_mano

from ..utils.funciones_aux import aux_generar_baraja_inicial, repartir_cartas

from ..models.catalogo_tickets import TICKETS, PROBABILIDAD_TICKET, PROBABILIDAD_TICKET_CLASE, PROBABILIDAD_TICKET_CLASE_ULTIMO

from ..selectors.ticket_selector import get_tickets_clase_0, get_tickets_clase_1, get_tickets_clase_2, get_tickets_clase_3

from ..selectors.partida_selector import get_colores_jugadores, get_colores_ordenados_por_puntuacion, get_colores_ordenados_por_puntuacion_con_ticket, get_partida_by_id, get_partida_usuario_by_partida_and_color, get_partida_usuario_by_partida_and_usuario

from ..services.resumen_mano_service import recopilar_ticket_usado


def repartir_tickets(partida_id):
    partida_num_jug = get_partida_by_id(partida_id).first().num_jugadores
    partida_especiales = get_partida_by_id(partida_id).first().cartas_especiales
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
    if not partida_usuario or partida_usuario.abandono:
        raise PermissionError("No participas en la partida.")

    if partida_usuario.ticket != ticket:
        raise ValueError("No tienes este ticket.")
    
    partida = get_partida_by_id(partida_id).first()
    if not partida.tickets:
        raise PermissionError("No se pueden usar tickets en esta partida.")
    if partida.turno_actual != partida_usuario.color:
        raise PermissionError("No es tu turno para usar un ticket.")
    ronda_actual = get_rondas_de_mano(get_mano_actual(partida_id).id)[-1]

    if TICKETS[ticket]["usable"] == "ronda" and ronda_actual.num < 1:
        raise PermissionError("No puedes usar este ticket en la ronda actual.")
    elif TICKETS[ticket]["usable"] == "cambios" and (ronda_actual.num > 0 or ronda_actual.cambios > 0):
        raise PermissionError("No puedes usar este ticket en la ronda actual.")


    if ticket.startswith("ticket_cb"):
        aux_usar_ticket_cb(partida_id, ticket, partida_usuario)
    elif ticket.startswith("ticket_ic"):
        aux_usar_ticket_ic(partida_id, ticket, partida_usuario)
    elif ticket.startswith("ticket_pp"):
        aux_usar_ticket_pp(partida_id, ticket, partida_usuario)
    elif ticket.startswith("ticket_rp"):
        aux_usar_ticket_rp(partida_id, ticket, partida_usuario)
    elif ticket.startswith("ticket_cp"):
        aux_usar_ticket_cp(ticket, partida_usuario)
    elif ticket.startswith("ticket_ro"):
        aux_usar_ticket_ro(partida_id, ticket, partida_usuario)
    elif ticket.startswith("ticket_rt"):
        aux_usar_ticket_rt(partida_id, ticket, partida_usuario)
    else:
        raise ValueError("Ticket no reconocido.")

    # Después de usar el ticket, se elimina del jugador.
    if not ticket.startswith("ticket_rt"): # En caso de robo de ticket NO eliminamos el ticket
        partida_usuario.ticket = None
        partida_usuario.save(update_fields=["ticket"])

    # Recopilar el uso
    mano_id = get_mano_actual(partida_id).id
    recopilar_ticket_usado(mano_id, ronda_actual.num, partida_usuario.color, ticket)

def aux_usar_ticket_cb(partida_id, ticket, jugador_actor):
    partida = get_partida_by_id(partida_id).first()
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

    for jugador in get_colores_jugadores(partida_id):
        partida_usuario = get_partida_usuario_by_partida_and_color(partida_id, jugador)
        partida_usuario.cartas = []
        partida_usuario.carta_comodin = None
        partida_usuario.save(update_fields=["cartas", "carta_comodin"])

    repartir_cartas(jugador_actor.usuario, partida_id)

def aux_usar_ticket_ic(partida_id, ticket, jugador_actor):
    dic_colores = get_colores_ordenados_por_puntuacion(partida_id)
    for _, colores in dic_colores.items():
        if jugador_actor.color in colores:
            colores.remove(jugador_actor.color)
            break

    if ticket.endswith("azar"):
        puntos_validos = [
            puntos
            for puntos, colores in dic_colores.items()
            if colores
        ]
        puntos = random.choice(puntos_validos)
        color_objetivo = random.choice(dic_colores[puntos])
    elif ticket.endswith("primero"):
        puntos = max(
            puntos for puntos, colores in dic_colores.items()
            if colores
        )
        color_objetivo = random.choice(dic_colores[puntos])
    else:
        raise ValueError("Ticket no reconocido.")

    actor = get_partida_usuario_by_partida_and_color(partida_id, jugador_actor.color)
    comodin_actor = actor.carta_comodin
    objetivo = get_partida_usuario_by_partida_and_color(partida_id, color_objetivo)
    comodin_objetivo = objetivo.carta_comodin
    intercambio = comodin_actor # variable de intercambio para almacenar el comodin del actor temporalmente
    actor.carta_comodin = comodin_objetivo
    objetivo.carta_comodin = intercambio

    actor.save(update_fields=["carta_comodin"])
    objetivo.save(update_fields=["carta_comodin"])

def aux_usar_ticket_pp(partida_id, ticket, jugador_actor):
    dic_colores = get_colores_ordenados_por_puntuacion(partida_id)
    for puntuacion, colores in dic_colores.items():
        if jugador_actor.color in colores:
            colores.remove(jugador_actor.color)
            break

    if "2" in ticket:
        puntos_a_perder = 2
    elif "4" in ticket:
        puntos_a_perder = 4
    elif "6" in ticket:
        puntos_a_perder = 6
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
                jugador.puntos -= puntos_a_perder
                jugador.save(update_fields=["puntos"])
    else:
        if ticket.endswith("azar"):
            puntos_validos = [
                puntos
                for puntos, colores in dic_colores.items()
                if colores
            ]
            puntos = random.choice(puntos_validos)
            color_objetivo = random.choice(dic_colores[puntos])
        elif ticket.endswith("primero"):
            puntos = max(
                puntos for puntos, colores in dic_colores.items()
                if colores
            )
            color_objetivo = random.choice(dic_colores[puntos])
        else:
            raise ValueError("Ticket no reconocido.")
        objetivo = get_partida_usuario_by_partida_and_color(partida_id, color_objetivo)
        objetivo.puntos -= puntos_a_perder
        objetivo.save(update_fields=["puntos"])

def aux_usar_ticket_rp(partida_id, ticket, jugador_actor):

    aux_usar_ticket_pp(partida_id, ticket, jugador_actor)
    if ticket.endswith("todos"):
        jugador_actor.puntos += 2 * (len(get_colores_jugadores(partida_id)) - 1)
    else:
        jugador_actor.puntos += 2
    jugador_actor.save(update_fields=["puntos"])

def aux_usar_ticket_cp(ticket, jugador_actor):

    if ticket.endswith("_2"):
        jugador_actor.puntos += 2
    elif ticket.endswith("_4"):
        jugador_actor.puntos += 4
    elif ticket.endswith("_6"):
        jugador_actor.puntos += 6
    elif ticket.endswith("_10"):
        jugador_actor.puntos += 10
    else:
        raise ValueError("Ticket no reconocido.")

    jugador_actor.save(update_fields=["puntos"])

def aux_usar_ticket_ro(partida_id, ticket, jugador_actor):
    dic_colores = get_colores_ordenados_por_puntuacion(partida_id)
    for puntuacion, colores in dic_colores.items():
        if jugador_actor.color in colores:
            colores.remove(jugador_actor.color)
            break

    if ticket.endswith("azar"):
        puntos_validos = [
            puntos
            for puntos, colores in dic_colores.items()
            if colores
        ]
        puntos = random.choice(puntos_validos)
        color_objetivo = random.choice(dic_colores[puntos])
    elif ticket.endswith("primero"):
        puntos = max(
            puntos for puntos, colores in dic_colores.items()
            if colores
        )
        color_objetivo = random.choice(dic_colores[puntos])
    else:
        raise ValueError("Ticket no reconocido.")

    objetivo = get_partida_usuario_by_partida_and_color(partida_id, color_objetivo)
    objetivo.retirado = True
    objetivo.save(update_fields=["retirado"])

def aux_usar_ticket_rt(partida_id, ticket, jugador_actor):
    dic_colores = get_colores_ordenados_por_puntuacion_con_ticket(partida_id)
    for puntuacion, colores in dic_colores.items():
        if jugador_actor.color in colores:
            colores.remove(jugador_actor.color)
            break
    if dic_colores is None or len(dic_colores) == 0:
        raise ValueError("No hay jugadores con tickets para robar.")

    if ticket.endswith("azar"):
        puntos_validos = [
            puntos
            for puntos, colores in dic_colores.items()
            if colores
        ]
        puntos = random.choice(puntos_validos)
        color_objetivo = random.choice(dic_colores[puntos])
    elif ticket.endswith("primero"):
        puntos = max(
            puntos for puntos, colores in dic_colores.items()
            if colores
        )
        color_objetivo = random.choice(dic_colores[puntos])
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

    actor = get_partida_usuario_by_partida_and_color(partida_id, jugador_actor.color)
    objetivo = get_partida_usuario_by_partida_and_color(partida_id, color_objetivo)
    actor.ticket = objetivo.ticket
    actor.save(update_fields=["ticket"])
    objetivo.ticket = None
    objetivo.save(update_fields=["ticket"])