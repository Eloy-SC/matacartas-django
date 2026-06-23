from sqlite3 import IntegrityError
from django.utils import timezone

from ..models.partida_usuario import PartidaUsuario

from ..selectors.rango_selector import get_rango_by_id
from ..utils.exceptions import RegistrationError

from ..models.partida import Partida
from ..selectors.partida_selector import *


def listar_partidas_publicas(
        actor, 
        *, 
        page, 
        page_size,
    search=None,
        nombre=None,
        num_jugadores=None,
        rango_minimo_id=None,
        rango_maximo_id=None,
        empezada=None,
        order_by="id",
        order_dir="asc",
        ):
    """
    Devuelve una lista paginada de partidas públicas en juego o en sala de espera.
    """

    if not actor.is_authenticated:
        raise PermissionError("No tienes permiso para listar las partidas públicas")
    
    allowed_order_fields = {"id", "nombre", "num_jugadores", "rango_minimo_id", "rango_maximo_id", "fecha_creacion", "fecha_inicio", "fecha_fin"}
    order_field = order_by if order_by in allowed_order_fields else "id"
    order_prefix = "-" if order_dir == "desc" else ""
    ordering = f"{order_prefix}{order_field}"
    
    total = get_partidas_publicas_count(
        search=search,
        nombre=nombre,
        num_jugadores=num_jugadores,
        rango_minimo_id=rango_minimo_id,
        rango_maximo_id=rango_maximo_id,
        empezada=empezada
    )
    offset = (page - 1) * page_size
    items = list(
        get_partidas_publicas_paginated(
            offset, 
            page_size,
            search=search,
            nombre=nombre,
            num_jugadores=num_jugadores,
            rango_minimo_id=rango_minimo_id,
            rango_maximo_id=rango_maximo_id,
            empezada=empezada,
            ordering=ordering
        )
    )
    total_pages = max(1, (total + page_size - 1) // page_size)

    rango_nombre_cache = {}

    def _get_rango_nombre(rango_id):
        if rango_id is None:
            return None
        if rango_id not in rango_nombre_cache:
            rango = get_rango_by_id(rango_id)
            rango_nombre_cache[rango_id] = rango.nombre if rango else None
        return rango_nombre_cache[rango_id]

    items_payload = []
    for partida in items:
        id_partida = partida.get("id")
        rango_minimo_nombre = _get_rango_nombre(partida.get("rango_minimo_id"))
        rango_maximo_nombre = _get_rango_nombre(partida.get("rango_maximo_id"))

        items_payload.append(
            {
                "id": id_partida,
                "nombre": partida.get("nombre"),
                "jugadores_maximos": partida.get("num_jugadores"),
                "rango_minimo": rango_minimo_nombre,
                "rango_maximo": rango_maximo_nombre,
                "jugadores_actuales": get_jugadores_actuales_de_partida_count(id_partida),
                "estado": get_estado_de_partida(id_partida),
            }
        )

    return {
        "items": items_payload,
        "page": page,
        "page_size": page_size,
        "total": total,
        "total_pages": total_pages,
    }

def crear_partida(actor, nombre, num_jugadores, privada, clave, longitud, cartas_invencibles, tiempo_max_turno, rango_minimo_id=None, rango_maximo_id=None):
    """
    Crea una nueva partida con los parámetros especificados.
    """

    if not actor.is_authenticated:
        raise PermissionError("No tienes permiso para crear una partida")
    
    if get_partida_by_nombre(nombre):
        raise RegistrationError({"nombre": ["El nombre ya existe"]})
    if privada:
        if not clave:
            raise RegistrationError({"clave": ["Falta la clave para la partida privada"]})
        else:
            if get_partida_by_clave(clave):
                raise RegistrationError({"clave": ["La clave ya existe"]})
    if not privada:
        if clave:
            raise RegistrationError({"clave": ["No se puede asignar una clave a una partida pública"]})
    
    if num_jugadores < 2:
        raise ValueError("El número de jugadores debe ser al menos 2")
    if num_jugadores > 6:
        raise ValueError("El número de jugadores no puede ser mayor a 6")
    
    if longitud not in Partida.LongitudPartida.values:
        raise ValueError("La longitud de la partida no es válida")
    
    if tiempo_max_turno < 20:
        raise ValueError("El tiempo máximo por turno debe ser al menos 20 segundos")
    if tiempo_max_turno > 180:
        raise ValueError("El tiempo máximo por turno no puede ser mayor a 180 segundos (3 minutos)")
    
    rango_minimo = get_rango_by_id(rango_minimo_id) if rango_minimo_id is not None else None
    rango_maximo = get_rango_by_id(rango_maximo_id) if rango_maximo_id is not None else None
    if rango_minimo and rango_maximo:
        if rango_minimo.puntos_minimos > rango_maximo.puntos_minimos:
            raise ValueError("El rango mínimo no puede ser mayor que el rango máximo")
        if actor.puntuacion > rango_maximo.puntos_maximos or actor.puntuacion < rango_minimo.puntos_minimos:
            raise PermissionError("Tu rango se encuentra fuera del intervalo permitido para esta partida")
        
    if get_usuario_participa_en_partida_activa(actor.id):
        raise ValueError("Ya estás participando en una partida activa")
    
    partida = Partida(
        nombre=nombre,
        num_jugadores=num_jugadores,
        privada=privada,
        clave=clave,
        longitud=longitud,
        cartas_invencibles=cartas_invencibles,
        tiempo_max_turno=tiempo_max_turno,
        rango_minimo_id=rango_minimo_id,
        rango_maximo_id=rango_maximo_id,
    )

    partida_usuario = PartidaUsuario(
        partida=partida,
        usuario=actor,
        creador=True
    )
    
    try:
        partida.save()
        partida_usuario.save()
    except IntegrityError:
        raise RegistrationError({"detail": ["No se pudo crear la partida"]})

    return partida

def editar_partida(actor, partida_id, nombre, num_jugadores, privada, clave, longitud, cartas_invencibles, tiempo_max_turno, rango_minimo_id=None, rango_maximo_id=None):
    """
    Edita una partida existente con los nuevos parámetros especificados.
    """

    if not actor.is_authenticated:
        raise PermissionError("No tienes permiso para editar una partida")
    
    partida = Partida.objects.filter(id=partida_id).first()
    if not partida:
        raise ValueError("La partida no existe")
    
    partida_usuario_actor = get_partida_usuario_by_partida_and_usuario(partida_id, actor.id)
    if not partida_usuario_actor or not partida_usuario_actor.creador:
        raise PermissionError("No tienes permiso para editar esta partida")

    partida_by_nombre = get_partida_by_nombre(nombre).first()
    if partida_by_nombre and partida_by_nombre.id != partida_id:
        raise RegistrationError({"nombre": ["El nombre ya existe"]})
    if privada:
        if not clave:
            raise RegistrationError({"clave": ["Falta la clave para la partida privada"]})
        else:
            partida_by_clave = get_partida_by_clave(clave).first()
            if partida_by_clave and partida_by_clave.id != partida_id:
                raise RegistrationError({"clave": ["La clave ya existe"]})
    if not privada:
        if clave:
            raise RegistrationError({"clave": ["No se puede asignar una clave a una partida pública"]})
    
    if num_jugadores < 2:
        raise ValueError("El número de jugadores debe ser al menos 2")
    if num_jugadores > 6:
        raise ValueError("El número de jugadores no puede ser mayor a 6")
    if num_jugadores < get_jugadores_actuales_de_partida_count(partida_id):
        raise ValueError("El número de jugadores no puede ser menor que el número de jugadores actuales en la partida")
    
    if longitud not in Partida.LongitudPartida.values:
        raise ValueError("La longitud de la partida no es válida")
    
    if tiempo_max_turno < 20:
        raise ValueError("El tiempo máximo por turno debe ser al menos 20 segundos")
    if tiempo_max_turno > 180:
        raise ValueError("El tiempo máximo por turno no puede ser mayor a 180 segundos (3 minutos)")
    
    comprobar_rangos(rango_minimo_id, rango_maximo_id, partida_id)
    
    partida.nombre = nombre
    partida.num_jugadores = num_jugadores
    partida.privada = privada
    partida.clave = clave
    partida.longitud = longitud
    partida.cartas_invencibles = cartas_invencibles
    partida.tiempo_max_turno = tiempo_max_turno
    partida.rango_minimo_id = rango_minimo_id
    partida.rango_maximo_id = rango_maximo_id

    try:
        partida.save()
    except IntegrityError:
        raise RegistrationError({"detail": ["No se pudo crear la partida"]})

    return partida

def comprobar_rangos(rango_minimo_id, rango_maximo_id, partida_id):
    rango_minimo = get_rango_by_id(rango_minimo_id) if rango_minimo_id is not None else None
    rango_maximo = get_rango_by_id(rango_maximo_id) if rango_maximo_id is not None else None
    if rango_minimo and rango_maximo:
        if rango_minimo.puntos_minimos > rango_maximo.puntos_minimos:
            raise ValueError("El rango mínimo no puede ser mayor que el rango máximo")
    if rango_minimo or rango_maximo:
        for jugador in get_jugadores_actuales_de_partida(partida_id):
            if rango_maximo:
                if jugador["puntuacion"] > rango_maximo.puntos_maximos:
                    raise PermissionError("Hay jugadores en la partida que se encuentran fuera del intervalo permitido por los nuevos rangos")
            if rango_minimo:
                if jugador["puntuacion"] < rango_minimo.puntos_minimos:
                    raise PermissionError("Hay jugadores en la partida que se encuentran fuera del intervalo permitido por los nuevos rangos")

def get_partida_como_jugador(actor, partida_id):
    """
    Devuelve la partida con el ID especificado si el actor es un jugador de la misma.
    """

    if not get_jugador_participa_en_partida(partida_id, actor.id):
        raise PermissionError("No tienes permiso para ver esta partida")
    
    partida = Partida.objects.filter(id=partida_id).first()
    if not partida:
        raise ValueError("La partida no existe")
    
    return partida

def get_jugadores_partida(actor, partida_id):
    """
    Devuelve una lista de los jugadores que están actualmente en la partida.
    """

    if not actor.is_authenticated:
        raise PermissionError("No tienes permiso para ver los jugadores de esta partida")
    
    jugadores = get_jugadores_actuales_de_partida(partida_id)
    if jugadores is None:
        raise ValueError("La partida no existe")
    
    return jugadores

def get_partida_jugador(actor, partida_id):
    """
    Devuelve la relación entre el jugador y la partida si el jugador está participando en la misma.
    """

    if not actor.is_authenticated:
        raise PermissionError("No tienes permiso para ver esta partida")
    
    partida_usuario = get_partida_usuario_by_partida_and_usuario(partida_id, actor.id)
    if not partida_usuario:
        raise ValueError("No estás participando en esta partida")
    
    return partida_usuario

def abandonar_partida(actor, partida_id):
    """
    Permite a un jugador abandonar una partida en la que está participando.
    """
    
    partida_usuario = get_partida_usuario_by_partida_and_usuario(partida_id, actor.id)
    if not partida_usuario:
        raise ValueError("No estás participando en esta partida")
    if partida_usuario.creador:
        aux_asignar_nuevo_creador(partida_id, actor.id)
    
    partida_usuario.delete()

    if get_jugadores_actuales_de_partida_count(partida_id) <= 0:
        partida = get_partida_by_id(partida_id).first()
        if partida:
            partida.delete()

def aux_asignar_nuevo_creador(partida_id, usuario_id):
    """
    Asigna un nuevo creador a la partida si el creador actual abandona la misma.
    """

    partida = get_partida_by_id(partida_id).first()
    if not partida:
        raise ValueError("La partida no existe")
    
    jugadores = get_jugadores_actuales_de_partida(partida_id)
    if not jugadores:
        return
    
    nuevo_creador = None
    for jugador in jugadores:
        if jugador["id"] != usuario_id:
            nuevo_creador = jugador
            break
    
    if not nuevo_creador:
        return
    
    partida_usuario = get_partida_usuario_by_partida_and_usuario(partida_id, nuevo_creador["id"])
    if not partida_usuario:
        raise ValueError("El nuevo creador no está participando en esta partida")
    
    partida_usuario.creador = True
    partida_usuario.save()

def unirse_a_partida_publica(actor, partida_id):
    """
    Permite a un jugador unirse a una partida pública en la que aún hay plazas disponibles.
    """

    if not actor.is_authenticated:
        raise PermissionError("No tienes permiso para unirte a esta partida")
    
    partida = get_partida_by_id(partida_id).first()
    if not partida:
        raise ValueError("La partida no existe")
    
    if get_jugador_participa_en_partida(partida_id, actor.id):
        raise ValueError("Ya estás participando en esta partida")
    
    jugadores_actuales = get_jugadores_actuales_de_partida_count(partida_id)
    if jugadores_actuales >= partida.num_jugadores:
        raise ValueError("La partida ya está llena")
    
    rango_minimo_puntos = partida.rango_minimo.puntos_minimos if partida.rango_minimo else None
    rango_maximo_puntos = partida.rango_maximo.puntos_maximos if partida.rango_maximo else None
    if rango_minimo_puntos is not None and actor.puntuacion < rango_minimo_puntos:
        raise PermissionError("Tu rango es demasiado bajo para unirte a esta partida")
    if rango_maximo_puntos is not None and actor.puntuacion > rango_maximo_puntos:
        raise PermissionError("Tu rango es demasiado alto para unirte a esta partida")
    
    if get_usuario_participa_en_partida_activa(actor.id):
        raise ValueError("Ya estás participando en una partida activa")
    
    partida_usuario = PartidaUsuario(
        partida=partida,
        usuario=actor,
        creador=False
    )
    
    try:
        partida_usuario.save()
    except IntegrityError:
        raise RegistrationError({"detail": ["No se pudo unir a la partida"]})
    
def unirse_a_partida_privada(actor, clave):
    """
    Permite a un jugador unirse a una partida privada con la clave correcta.
    """

    if not actor.is_authenticated:
        raise PermissionError("No tienes permiso para unirte a esta partida")
    
    partida = get_partida_by_clave(clave).first()
    if not partida:
        raise ValueError("La partida no existe. Revisa que la clave sea correcta")
    
    if get_jugador_participa_en_partida(partida.id, actor.id):
        raise ValueError("Ya estás participando en esta partida")
    
    jugadores_actuales = get_jugadores_actuales_de_partida_count(partida.id)
    if jugadores_actuales >= partida.num_jugadores:
        raise ValueError("La partida ya está llena")
    
    rango_minimo_puntos = partida.rango_minimo.puntos_minimos if partida.rango_minimo else None
    rango_maximo_puntos = partida.rango_maximo.puntos_maximos if partida.rango_maximo else None
    if rango_minimo_puntos is not None and actor.puntuacion < rango_minimo_puntos:
        raise PermissionError("Tu rango es demasiado bajo para unirte a esta partida")
    if rango_maximo_puntos is not None and actor.puntuacion > rango_maximo_puntos:
        raise PermissionError("Tu rango es demasiado alto para unirte a esta partida")
    
    if get_usuario_participa_en_partida_activa(actor.id):
        raise ValueError("Ya estás participando en una partida activa")
    
    partida_usuario = PartidaUsuario(
        partida=partida,
        usuario=actor,
        creador=False
    )
    
    try:
        partida_usuario.save()
    except IntegrityError:
        raise RegistrationError({"detail": ["No se pudo unir a la partida"]})

def toggle_listo(actor, partida_id):
    """
    Permite a un jugador marcarse como listo/no listo en una partida en la que está participando.
    """

    partida_usuario = get_partida_usuario_by_partida_and_usuario(partida_id, actor.id)
    if not partida_usuario:
        raise ValueError("No estás participando en esta partida")
    
    if partida_usuario.listo:
        partida_usuario.listo = False
    else:
        partida_usuario.listo = True
    partida_usuario.save()

def expulsar_jugador(actor, partida_id, jugador_id):
    """
    Permite al creador de la partida expulsar a un jugador de la misma.
    """

    partida_usuario_actor = get_partida_usuario_by_partida_and_usuario(partida_id, actor.id)
    if not partida_usuario_actor or not partida_usuario_actor.creador:
        raise PermissionError("No tienes permiso para expulsar jugadores de esta partida")
    
    partida_usuario_jugador = get_partida_usuario_by_partida_and_usuario(partida_id, jugador_id)
    if not partida_usuario_jugador:
        raise ValueError("El jugador no está participando en esta partida")
    
    if partida_usuario_jugador.creador:
        raise ValueError("No puedes expulsar al creador de la partida")
    
    partida = get_partida_by_id(partida_id).first()
    if not partida:
        raise ValueError("La partida no existe")
    if partida.fecha_inicio is not None:
        raise ValueError("No puedes expulsar jugadores de una partida que ya ha comenzado")
    
    partida_usuario_jugador.delete()

def iniciar_partida(actor, partida_id):
    """
    Permite al creador de la partida iniciar la misma si todos los jugadores están listos.
    """

    partida = get_partida_by_id(partida_id).first()
    if not partida:
        raise ValueError("La partida no existe")

    partida_usuario_actor = get_partida_usuario_by_partida_and_usuario(partida_id, actor.id)
    if not partida_usuario_actor or not partida_usuario_actor.creador:
        raise PermissionError("No tienes permiso para iniciar esta partida")
    
    jugadores_conectados = get_jugadores_actuales_de_partida_count(partida_id)
    if jugadores_conectados < partida.num_jugadores:
        raise ValueError(f"No hay suficientes jugadores para iniciar la partida, se necesitan {partida.num_jugadores}.")
    
    jugadores = get_jugadores_actuales_de_partida(partida_id)
    for jugador in jugadores:
        if not jugador["listo"]:
            raise ValueError("Todos los jugadores deben estar listos para iniciar la partida")
    
    if partida.fecha_inicio is not None:
        raise ValueError("La partida ya ha comenzado")
    
    partida.fecha_inicio = timezone.now()
    partida.save()