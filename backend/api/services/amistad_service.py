

from ..selectors.amistad_selector import count_amigos, list_amigos_paginated


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



