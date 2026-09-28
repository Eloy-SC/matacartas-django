from ..selectors.partida_selector import get_partida_by_id

from ..selectors.notificacion_selector import count_notificaciones, get_invitacion_partida_by_id, get_invitacion_partida_by_usuario_ids, get_solicitud_amistad_by_id, get_solicitud_amistad_by_usuario_ids, list_notificaciones_paginated
from ..selectors.amistad_selector import get_amistad_by_usuario_ids

from ..models.notificacion import InvitacionPartida, SolicitudAmistad
from ..models import Amistad

def listar_notificaciones(actor, page=1, page_size=10):
    if not actor.is_active:
        raise PermissionError("No tienes permiso para listar tus notificaciones")

    offset = (page - 1) * page_size
    total = count_notificaciones(actor.id)
    items = list(list_notificaciones_paginated(actor.id, offset, page_size))
    return {
        "items": items,
        "page": page,
        "page_size": page_size,
        "total": total,
        "total_pages": max(1, (total + page_size - 1) // page_size),
    }

def enviar_solicitud_amistad(actor, objetivo_id):
    if not actor.is_active:
        raise PermissionError("No tienes permiso para enviar solicitudes de amistad")

    if actor.id == objetivo_id:
        raise ValueError("No puedes enviarte una solicitud de amistad a ti mismo")

    # Verificar si ya existe una amistad entre los usuarios
    amistad_existente = get_amistad_by_usuario_ids(actor.id, objetivo_id)
    if amistad_existente:
        raise ValueError("Ya eres amigo de este usuario")

    # Verificar si ya existe una solicitud de amistad pendiente
    solicitud_existente = get_solicitud_amistad_by_usuario_ids(actor.id, objetivo_id)
    if solicitud_existente:
        raise ValueError("Ya has enviado una solicitud de amistad a este usuario")

    # Crear la nueva solicitud de amistad
    nueva_solicitud = SolicitudAmistad.objects.create(
        receptor_id=objetivo_id,
        emisor_id=actor.id
    )
    return nueva_solicitud

def contestar_solicitud_amistad(actor, solicitud_id, aceptar=False):
    if not actor.is_active:
        if aceptar:
            raise PermissionError("No tienes permiso para aceptar solicitudes de amistad")
        else:
            raise PermissionError("No tienes permiso para rechazar solicitudes de amistad")

    solicitud = get_solicitud_amistad_by_id(solicitud_id)
    if not solicitud:
        raise ValueError("No se encontró la solicitud de amistad")
    
    # Si se acepta la solicitud, crear la amistad entre los usuarios
    if aceptar:
        Amistad.objects.create(usuario1_id=solicitud.emisor_id, usuario2_id=solicitud.receptor_id)

    # Eliminar la solicitud de amistad
    solicitud.delete()

def enviar_invitacion_partida(actor, objetivo_id, partida_id):
    if not actor.is_active:
        raise PermissionError("No tienes permiso para enviar invitaciones de partida")

    if actor.id == objetivo_id:
        raise ValueError("No puedes enviarte una solicitud de amistad a ti mismo")

    partida = get_partida_by_id(partida_id)
    if not partida:
        raise ValueError("No se encontró la partida especificada")

    invitacion_existente = get_invitacion_partida_by_usuario_ids(actor.id, objetivo_id)
    if invitacion_existente:
        raise ValueError("Ya has enviado una invitación de partida a este usuario")

    # Crear la nueva invitación de partida
    nueva_invitacion = InvitacionPartida.objects.create(
        receptor_id=objetivo_id,
        emisor_id=actor.id,
        partida_id=partida_id
    )
    return nueva_invitacion

def contestar_invitacion_partida(actor, invitacion_id, aceptar=False):
    if not actor.is_active:
        if aceptar:
            raise PermissionError("No tienes permiso para aceptar invitaciones de partida")
        else:
            raise PermissionError("No tienes permiso para rechazar invitaciones de partida")

    invitacion = get_invitacion_partida_by_id(invitacion_id)
    if not invitacion:
        raise ValueError("No se encontró la invitación de partida")
    
    # Si se acepta la invitación, agregar al usuario a la partida
    if aceptar:
        partida = get_partida_by_id(invitacion.partida_id)
        if not partida:
            raise ValueError("No se encontró la partida especificada")

    # Eliminar la invitación de partida
    invitacion.delete()
    