

from ..selectors.amistad_selector import count_amigos, count_usuarios_disponibles_amistad, get_amistad_by_usuario_ids, list_amigos_paginated, list_usuarios_disponibles_amistad_paginated

def listar_usuarios_busqueda_amistad(actor, page=1, page_size=10, search=None):
    if not actor.is_active:
        raise PermissionError("No tienes permiso para buscar usuarios")

    total = count_usuarios_disponibles_amistad(actor.id, search=search)
    offset = (page - 1) * page_size
    items = list(list_usuarios_disponibles_amistad_paginated(actor.id, offset, page_size, search=search))
    return {
        "items": items,
        "page": page,
        "page_size": page_size,
        "total": total,
        "total_pages": max(1, (total + page_size - 1) // page_size),
    }

def listar_amigos_paginated(actor, page=1, page_size=10, search=None):
    if not actor.is_active:
        raise PermissionError("No tienes permiso para listar tus amigos")

    total = count_amigos(actor.id, search=search)
    offset = (page - 1) * page_size
    items = list(list_amigos_paginated(actor.id, offset, page_size, search=search))
    return {
        "items": items,
        "page": page,
        "page_size": page_size,
        "total": total,
        "total_pages": max(1, (total + page_size - 1) // page_size),
    }

def eliminar_amigo(actor, amigo_id):
    if not actor.is_active:
        raise PermissionError("No tienes permiso para eliminar amigos")

    amistad = get_amistad_by_usuario_ids(actor.id, amigo_id)

    if not amistad:
        raise ValueError("No se encontró la amistad con el usuario especificado")

    amistad.delete()



