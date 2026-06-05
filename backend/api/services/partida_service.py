from sqlite3 import IntegrityError

from ..selectors.rango_selector import get_rango_by_id
from ..utils.exceptions import RegistrationError

from ..models.partida import Partida
from ..selectors.partida_selector import get_estado_de_partida, get_jugadores_actuales_de_partida, get_partidas_by_clave, get_partidas_by_nombre, get_partidas_publicas_count, get_partidas_publicas_paginated


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
                "jugadores_actuales": get_jugadores_actuales_de_partida(id_partida),
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
    
    if get_partidas_by_nombre(nombre).exists():
        raise RegistrationError({"nombre": ["El nombre ya existe"]})
    if privada:
        if not clave:
            raise RegistrationError({"clave": ["Falta la clave para la partida privada"]})
        else:
            if get_partidas_by_clave(clave).exists():
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
    if rango_minimo and rango_maximo and rango_minimo.puntos_minimos > rango_maximo.puntos_minimos:
        raise ValueError("El rango mínimo no puede ser mayor que el rango máximo")
    
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
    
    try:
        partida.save()
    except IntegrityError:
        raise RegistrationError({"detail": ["No se pudo crear la partida"]})

    return partida