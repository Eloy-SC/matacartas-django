from ..models.ronda import Ronda

from ..selectors.ronda_selector import get_ronda_cambios, get_rondas_de_mano
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
                carta_comodin=jugador.get("carta_comodin")
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
        disposicion_jugadores=partida.disposicion_jugadores,
        turno_actual=partida.turno_actual,
        tiempo_max_turno=partida.tiempo_max_turno
    )

    mano_dto = ManoDTO(
        mano_id=mano.id,
        mano_num=mano.num
    ) if mano else None

    rondas_dto = [RondaDTO(
        ronda_id=ronda.id,
        ronda_num=ronda.num,
        cartas=ronda.cartas,
        cambiando=ronda.cambiando
    ) for ronda in rondas]

    mesa_dto = MesaDTO(
        partida=partida_dto,
        mano=mano_dto,
        rondas=rondas_dto,
        jugador=jugador_dto,
        contrincantes=contrincantes_dto
    )

    return mesa_dto

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
    
    partida.turno_actual = partida.disposicion_jugadores[0]  # El primer jugador en la disposición de jugadores comienza el turno
    
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
        ronda.cambiando = True
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

    ronda = Ronda(mano=get_mano_actual(partida_id), num=1, cartas={}, cambiando=False)  # Crea la ronda 1
    
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
        ronda.cambiando = False
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


    

    