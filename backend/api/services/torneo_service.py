from django.db import IntegrityError

from ..models.configuracion_global import ConfiguracionGlobal
from ..models.torneo import Torneo
from ..selectors.rango_selector import get_rango_by_id
from ..selectors.torneo_selector import (
    get_torneo_by_nombre,
    get_torneos_publicos_count,
    get_torneos_publicos_paginated,
)
from ..utils.exceptions import RegistrationError


def _get_estado_torneo(torneo):
    if torneo.get("fecha_fin") is not None:
        return "finalizado"
    if torneo.get("fecha_inicio") is not None:
        return "en_juego"
    if torneo.get("fecha_creacion") is not None:
        return "sala_espera"
    return "desconocido"


def listar_torneos_publicos(
    actor,
    *,
    page,
    page_size,
    search=None,
    nombre=None,
    rango_minimo_id=None,
    rango_maximo_id=None,
    empezado=None,
    order_by="id",
    order_dir="asc",
):
    if not actor.is_authenticated:
        raise PermissionError("No tienes permiso para listar los torneos")

    allowed_order_fields = {
        "id",
        "nombre",
        "rango_minimo_id",
        "rango_maximo_id",
        "fecha_creacion",
        "fecha_inicio",
        "fecha_fin",
        "num_jug_fin",
    }
    order_field = order_by if order_by in allowed_order_fields else "id"
    order_prefix = "-" if order_dir == "desc" else ""
    ordering = f"{order_prefix}{order_field}"

    total = get_torneos_publicos_count(
        search=search,
        nombre=nombre,
        rango_minimo_id=rango_minimo_id,
        rango_maximo_id=rango_maximo_id,
        empezado=empezado,
    )
    offset = (page - 1) * page_size
    items = list(
        get_torneos_publicos_paginated(
            offset,
            page_size,
            search=search,
            nombre=nombre,
            rango_minimo_id=rango_minimo_id,
            rango_maximo_id=rango_maximo_id,
            empezado=empezado,
            ordering=ordering,
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
    for torneo in items:
        items_payload.append(
            {
                "id": torneo.get("id"),
                "nombre": torneo.get("nombre"),
                "rango_minimo": _get_rango_nombre(torneo.get("rango_minimo_id")),
                "rango_maximo": _get_rango_nombre(torneo.get("rango_maximo_id")),
                "num_jug_fin": torneo.get("num_jug_fin"),
                "num_jug_sem": torneo.get("num_jug_sem"),
                "num_jug_cua": torneo.get("num_jug_cua"),
                "num_jug_oct": torneo.get("num_jug_oct"),
                "partidas_longitud": torneo.get("partidas_longitud"),
                "partidas_cartas_especiales": torneo.get("partidas_cartas_especiales"),
                "partidas_tickets": torneo.get("partidas_tickets"),
                "partidas_tiempo_max_turno": torneo.get("partidas_tiempo_max_turno"),
                "desempate_mayor_punt": torneo.get("desempate_mayor_punt"),
                "fecha_creacion": torneo.get("fecha_creacion"),
                "fecha_inicio": torneo.get("fecha_inicio"),
                "fecha_fin": torneo.get("fecha_fin"),
                "estado": _get_estado_torneo(torneo),
            }
        )

    return {
        "items": items_payload,
        "page": page,
        "page_size": page_size,
        "total": total,
        "total_pages": total_pages,
    }


def crear_torneo(
    actor,
    *,
    nombre,
    rango_minimo_id=None,
    rango_maximo_id=None,
    num_jug_fin=3,
    num_jug_sem=3,
    num_jug_cua=None,
    num_jug_oct=None,
    partidas_longitud=Torneo.LongitudPartidaDeTorneo.NORMAL,
    partidas_cartas_especiales=True,
    partidas_tickets=True,
    partidas_tiempo_max_turno=90,
    desempate_mayor_punt=True,
):
    if not actor.is_authenticated:
        raise PermissionError("No tienes permiso para crear un torneo")

    if get_torneo_by_nombre(nombre) is not None:
        raise RegistrationError({"nombre": ["El nombre ya existe"]})

    config = ConfiguracionGlobal.objects.get(pk=1)
    rango_minimo_creador = config.rango_minimo_crear_torneo
    if rango_minimo_creador is not None and actor.puntuacion < rango_minimo_creador.puntos_minimos:
        raise PermissionError("Tu puntuación es insuficiente para crear torneos")

    rango_minimo = get_rango_by_id(rango_minimo_id) if rango_minimo_id is not None else None
    rango_maximo = get_rango_by_id(rango_maximo_id) if rango_maximo_id is not None else None

    if rango_minimo and rango_maximo and rango_minimo.puntos_minimos > rango_maximo.puntos_minimos:
        raise ValueError("El rango mínimo no puede ser mayor que el rango máximo")

    if rango_minimo and actor.puntuacion < rango_minimo.puntos_minimos:
        raise PermissionError("Tu puntuación no alcanza el rango mínimo del torneo")
    if rango_maximo and actor.puntuacion > rango_maximo.puntos_maximos:
        raise PermissionError("Tu puntuación supera el rango máximo del torneo")

    torneo = Torneo(
        nombre=nombre,
        rango_minimo_id=rango_minimo_id,
        rango_maximo_id=rango_maximo_id,
        num_jug_fin=num_jug_fin,
        num_jug_sem=num_jug_sem,
        num_jug_cua=num_jug_cua,
        num_jug_oct=num_jug_oct,
        partidas_longitud=partidas_longitud,
        partidas_cartas_especiales=partidas_cartas_especiales,
        partidas_tickets=partidas_tickets,
        partidas_tiempo_max_turno=partidas_tiempo_max_turno,
        desempate_mayor_punt=desempate_mayor_punt,
    )

    try:
        torneo.save()
    except IntegrityError as e:
        msg = str(e)
        if "nombre" in msg:
            raise RegistrationError({"nombre": ["El nombre ya existe"]})
        raise RegistrationError({"detail": ["No se pudo crear el torneo"]})

    return torneo
