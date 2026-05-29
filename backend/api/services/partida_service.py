

from ..selectors.partida_selector import get_estado_de_partida, get_jugadores_actuales_de_partida, get_partidas_publicas_count, get_partidas_publicas_paginated


def listar_partidas_publicas(actor, *, page, page_size):
    """
    Devuelve una lista paginada de partidas públicas en juego o en sala de espera.
    """

    if not actor.is_authenticated:
        raise PermissionError("No tienes permiso para listar las partidas públicas")
    
    total = get_partidas_publicas_count()
    offset = (page - 1) * page_size
    items = list(get_partidas_publicas_paginated(offset, page_size))
    total_pages = max(1, (total + page_size - 1) // page_size)

    for partida in items:
        partida["jugadores_actuales"] = get_jugadores_actuales_de_partida(partida["id"])
        partida["estado"] = get_estado_de_partida(partida["id"])

    return {
        "items": items,
        "page": page,
        "page_size": page_size,
        "total": total,
        "total_pages": total_pages,
    }