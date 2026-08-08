from datetime import timezone

from ..models.mano import Mano
from ..models.ronda import Ronda
from ..models.catalogo_cartas import CATALOGO

from ..selectors.ronda_selector import get_carta_equivalente, get_cartas_lanzadas_en_mano, get_cartas_valiosas_utilizadas_en_mano, get_ronda_cambios, get_rondas_de_mano
from ..selectors.partida_selector import get_jugadores_actuales_de_partida, get_partida_by_id, get_partida_usuario_by_partida_and_usuario
from ..selectors.mano_selector import get_jugadores_en_mesa, get_mano_actual

from ..models.dtos import ContrincanteDTO, JugadorDTO, MesaDTO, RondaDTO, ManoDTO, PartidaDTO

from random import shuffle

from ..utils.funciones_aux import aux_siguiente_turno

def get_mesa(actor, partida_id):
    """
    Obtiene la información de la mesa de juego de una partida.
    """
    partida_usuario = get_partida_usuario_by_partida_and_usuario(partida_id, actor.id)
    if not partida_usuario:
        raise PermissionError("No participas en la partida.")
    
    partida = get_partida_by_id(partida_id).first()
    mano = get_mano_actual(partida_id)
    rondas = get_rondas_de_mano(mano.id) if mano else []

    contrincantes_dto = []
    jugador_dto = None

    jugadores = get_jugadores_actuales_de_partida(partida_id)
    for jugador in jugadores:
        if jugador["id"] == actor.id:
            jugador_dto = JugadorDTO(
                jugador_id=jugador["id"],
                nombre=jugador["nombre"],
                imagen=jugador["imagen"],
                color=jugador["color"],
                puntos=jugador["puntos"],
                cartas=jugador.get("cartas", []),
                carta_comodin=jugador.get("carta_comodin"),
                acumulador_kills=jugador.get("acumulador_kills", 0),
                acumulador_deaths=jugador.get("acumulador_deaths", 0),
            )
        else:
            contrincantes_dto.append(ContrincanteDTO(
                contrincante_id=jugador["id"],
                nombre=jugador["nombre"],
                imagen=jugador["imagen"],
                color=jugador["color"],
                puntos=jugador["puntos"],
                cartas_cant=len(jugador.get("cartas", [])),
                carta_comodin=jugador.get("carta_comodin") is not None
            ))

    partida_dto = PartidaDTO(
        partida_id=partida.id,
        baraja_cant=len(partida.baraja),
        longitud=partida.get_num_manos(),
        disposicion_jugadores=partida.disposicion_jugadores,
        turno_actual=partida.turno_actual,
        tiempo_max_turno=partida.tiempo_max_turno
    )

    mano_dto = ManoDTO(
        mano_id=mano.id,
        mano_num=mano.num,
        ganador=mano.ganador
    ) if mano else None

    rondas_dto = [RondaDTO(
        ronda_id=ronda.id,
        ronda_num=ronda.num,
        cartas=ronda.cartas,
        cambios=ronda.cambios
    ) for ronda in rondas]

    mesa_dto = MesaDTO(
        partida=partida_dto,
        mano=mano_dto,
        rondas=rondas_dto,
        jugador=jugador_dto,
        contrincantes=contrincantes_dto
    )

    return mesa_dto

def repartir_cartas(*args):
    """
    Reparte cartas a los jugadores de una partida.

    Compatible con llamadas `repartir_cartas(partida_id)` y
    `repartir_cartas(actor, partida_id)` para mantener compatibilidad
    con llamadas y tests que pasan el actor como primer argumento.
    """
    if len(args) == 1:
        partida_id = args[0]
    elif len(args) == 2:
        # signature reparto usado en algunos tests: (actor, partida_id)
        partida_id = args[1]
    else:
        raise TypeError("repartir_cartas expects (partida_id) or (actor, partida_id)")

    partida = get_partida_by_id(partida_id).first()
    jugadores = get_jugadores_en_mesa(partida_id, partida.disposicion_jugadores)

    shuffle(partida.baraja)
    vuelta = 1
    while vuelta < 5:
        for jugador in jugadores:
            if len(jugador.cartas) < 4:
                carta = partida.baraja.pop(0)  # Saca la primera carta de la baraja
                jugador.cartas.append(carta)  # Añade la carta a las cartas del jugador
            else:
                pass
        vuelta += 1

    # El primer jugador en la disposición de jugadores comienza el turno.
    try:
        partida.turno_actual = partida.disposicion_jugadores[0]
    except Exception:
        # Si no hay disposición definida, usar el primer jugador obtenido (si existe)
        if jugadores and len(jugadores) > 0:
            partida.turno_actual = jugadores[0].color
        else:
            partida.turno_actual = None

    # Guardar cambios
    for jugador in jugadores:
        jugador.save()
    partida.save()

def jugador_quiere_cambiar(actor, partida_id):
    """
    Indica que un jugador quiere cambiar cartas en la mano actual.
    """
    partida_usuario = get_partida_usuario_by_partida_and_usuario(partida_id, actor.id)
    if not partida_usuario:
        raise PermissionError("No participas en la partida.")
    if partida_usuario.color != get_partida_by_id(partida_id).first().turno_actual:
        raise PermissionError("No es tu turno.")
    if get_rondas_de_mano(get_mano_actual(partida_id).id)[-1].num != 0:
        raise ValueError("Esta no es la ronda de cambios.")

    partida = get_partida_by_id(partida_id).first()
    
    aux_siguiente_turno(partida)

    if partida.turno_actual == partida.disposicion_jugadores[0]: # Si el turno es el ult (sig turno = primer jugador), procedemos al cambio
        ronda = get_ronda_cambios(get_mano_actual(partida_id).id)
        ronda.cambios = 1
        ronda.save()
    

def jugador_no_quiere_cambiar(actor, partida_id):
    """
    Indica que un jugador no quiere cambiar cartas en la mano actual.
    """
    partida_usuario = get_partida_usuario_by_partida_and_usuario(partida_id, actor.id)
    if not partida_usuario:
        raise PermissionError("No participas en la partida.")
    if partida_usuario.color != get_partida_by_id(partida_id).first().turno_actual:
        raise PermissionError("No es tu turno.")
    if get_rondas_de_mano(get_mano_actual(partida_id).id)[-1].num != 0:
        raise ValueError("Esta no es la ronda de cambios.")

    partida = get_partida_by_id(partida_id).first()
    partida.turno_actual = partida.disposicion_jugadores[0]  # Reinicia el turno al primer jugador en la disposición de jugadores

    ronda = get_ronda_cambios(get_mano_actual(partida_id).id)
    ronda.cambios = 2
    ronda.save()
    partida.save()

def cambiar_cartas(actor, partida_id, cartas_a_cambiar):
    """
    Cambia las cartas de un jugador en la mano actual.
    """
    partida_usuario = get_partida_usuario_by_partida_and_usuario(partida_id, actor.id)
    if not partida_usuario:
        raise PermissionError("No participas en la partida.")
    if partida_usuario.color != get_partida_by_id(partida_id).first().turno_actual:
        raise PermissionError("No es tu turno.")
    if get_rondas_de_mano(get_mano_actual(partida_id).id)[-1].num != 0:
        raise ValueError("Esta no es la ronda de cambios.")

    partida = get_partida_by_id(partida_id).first()

    # Cambiar las cartas del jugador
    for carta in cartas_a_cambiar:
        if carta in partida_usuario.cartas:
            partida_usuario.cartas.remove(carta)
            partida.baraja.append(carta)  # Devuelve la carta a la baraja
        else:
            raise ValueError(f"No tienes la carta {carta} para cambiar.")

    # Repartir nuevas cartas al jugador
    while len(partida_usuario.cartas) < 4 and len(partida.baraja) > 0:
        nueva_carta = partida.baraja.pop(0)
        partida_usuario.cartas.append(nueva_carta)

    aux_siguiente_turno(partida)

    if partida.turno_actual == partida.disposicion_jugadores[0]: # Si el turno es el ult (sig turno = primer jugador), 
        ronda = get_ronda_cambios(get_mano_actual(partida_id).id)
        ronda.cambios = 0
        ronda.save()

    partida_usuario.save()
    partida.save()
    
def elegir_carta_comodin(actor, partida_id, carta_comodin):
    """
    Permite a un jugador elegir una carta comodín en la mano actual.
    """
    partida_usuario = get_partida_usuario_by_partida_and_usuario(partida_id, actor.id)
    if not partida_usuario:
        raise PermissionError("No participas en la partida.")
    if partida_usuario.color != get_partida_by_id(partida_id).first().turno_actual:
        raise PermissionError("No es tu turno.")
    if get_rondas_de_mano(get_mano_actual(partida_id).id)[-1].num != 0:
        raise ValueError("No puedes elegir carta comodin en mitad de la partida.")

    partida_usuario.cartas.pop(partida_usuario.cartas.index(carta_comodin))  # Elimina la carta comodín de las cartas del jugador
    partida_usuario.carta_comodin = carta_comodin  # Coloca la carta elegida como carta comodín del jugador
    partida_usuario.save()

    partida = get_partida_by_id(partida_id).first()
    aux_siguiente_turno(partida)

    if partida.turno_actual == partida.disposicion_jugadores[0]: # Si el turno es el ult (sig turno = primer jugador), crear ronda 1
        ronda = Ronda(mano=get_mano_actual(partida_id), num=1, cartas={}, cambios=2)
        ronda.save()

def get_datos_carta(actor, carta, partida_id):
    """
    Obtiene los datos de la carta comodín del jugador.
    """
    partida_usuario = get_partida_usuario_by_partida_and_usuario(partida_id, actor.id)
    if not partida_usuario:
        raise PermissionError("No participas en la partida.")

    carta_normalizada = carta.strip().upper() if isinstance(carta, str) else ""
    if carta_normalizada not in CATALOGO:
        raise ValueError("La carta no existe.")

    datos = {
        "nombre": carta_normalizada,
        "fuerza": CATALOGO[carta_normalizada]["fuerza"],
        "riqueza": CATALOGO[carta_normalizada]["riqueza"],
        "tipo": CATALOGO[carta_normalizada]["tipo"],
    }

    return datos

def siguiente_mano(actor, partida_id):
    """
    Inicia la siguiente mano en la partida.
    """
    partida_usuario = get_partida_usuario_by_partida_and_usuario(partida_id, actor.id)
    if not partida_usuario:
        raise PermissionError("No participas en la partida.")

    partida = get_partida_by_id(partida_id).first()
    if not partida:
        raise ValueError("Partida no encontrada.")

    mano_actual = get_mano_actual(partida_id)

    if mano_actual.num < partida.get_num_manos():


        for ronda in get_rondas_de_mano(mano_actual.id):
            for carta in ronda.cartas.values():
                if carta not in partida.baraja:
                    if not any(carta == "SEGADOR" for carta in get_cartas_lanzadas_en_mano(mano_actual.id)) \
                        or CATALOGO[carta]["tipo"] != "especial_val":
                        partida.baraja.append(carta)

        if any(carta == "SEGADOR" for carta in get_cartas_lanzadas_en_mano(mano_actual.id)):
            cartas_valiosas_utilizadas = get_cartas_valiosas_utilizadas_en_mano(mano_actual.id)
            for carta in cartas_valiosas_utilizadas:
                carta_equivalente = get_carta_equivalente(carta)
                partida.baraja.append(carta_equivalente)  # Añadir la carta equivalente a la baraja

        # Devolver comodines no utilizados a los jugadores correspondientes
        comodines_utilizados = get_rondas_de_mano(mano_actual.id)[-1].cartas
        for jugador in get_jugadores_actuales_de_partida(partida_id):
            carta_comodin = jugador.get("carta_comodin")
            if carta_comodin and carta_comodin not in comodines_utilizados:
                partida_usuario = get_partida_usuario_by_partida_and_usuario(partida_id, jugador["id"])
                if partida_usuario:
                    partida_usuario.cartas.append(jugador["carta_comodin"])
                    partida_usuario.carta_comodin = None
                    if carta_comodin == "MONEDERO_PECULIAR" and partida_usuario.eff_acum_monedero <= 15:
                        partida_usuario.eff_acum_monedero += 1
                    partida_usuario.save()


        # Crear nueva mano y su correspondiente ronda "0"
        nueva_mano = Mano(partida=partida, num=mano_actual.num + 1)
        nueva_mano.save()
        ronda_inicial = Ronda(mano=nueva_mano, num=0, cartas={}, cambios=0)
        ronda_inicial.save()

        # Repartir cartas
        repartir_cartas(partida_id)

    else: # Finalizar partida
        finalizar_partida(partida_id)

def finalizar_partida(partida_id):
    """
    Finaliza la partida y determina el ganador.
    """
    partida = get_partida_by_id(partida_id).first()
    if not partida:
        raise ValueError("Partida no encontrada.")

    # TODO: Implementar la lógica para determinar el ganador de la partida y actualizar los puntos de los jugadores.

    partida.fecha_fin = timezone.now()
    partida.save()