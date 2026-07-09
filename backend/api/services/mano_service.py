from ..selectors.ronda_selector import get_rondas_de_mano
from ..selectors.partida_selector import get_jugadores_actuales_de_partida, get_partida_by_id, get_partida_usuario_by_partida_and_usuario
from ..selectors.mano_selector import get_jugadores_en_mesa, get_mano_actual

from ..models.dtos import ContrincanteDTO, JugadorDTO, MesaDTO, RondaDTO, ManoDTO, PartidaDTO

from random import shuffle

def get_mesa(actor, partida_id):
    """
    Obtiene la información de la mesa de juego de una partida.
    """
    partida_usuario = get_partida_usuario_by_partida_and_usuario(partida_id, actor.id)
    if not partida_usuario:
        raise PermissionError("No participas en la partida.")
    
    partida = get_partida_by_id(partida_id).first()
    mano = get_mano_actual(partida_id)
    rondas = get_rondas_de_mano(mano.mano_id) if mano else []

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
        cartas=ronda.cartas
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
    
    # Guardar cambios
    for jugador in jugadores:
        jugador.save() 
    partida.save() 




    

    