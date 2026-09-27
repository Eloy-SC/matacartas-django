

from ..models.notificacion import InvitacionPartida, SolicitudAmistad

def count_notificaciones(usuario_id):
    return SolicitudAmistad.objects.filter(receptor_id=usuario_id).count() + InvitacionPartida.objects.filter(receptor_id=usuario_id).count()

def list_notificaciones_paginated(usuario_id, offset, limit):
    solicitudes = SolicitudAmistad.objects.filter(receptor_id=usuario_id).order_by('-id')[offset:offset + limit]
    invitaciones = InvitacionPartida.objects.filter(receptor_id=usuario_id).order_by('-id')[offset:offset + limit]
    notificaciones = solicitudes + invitaciones
    return [
        {
            "id": notificacion.id,
            "emisor_id": notificacion.emisor_id,
            "emisor_nombre": notificacion.emisor.nombre,
            "emisor_imagen": notificacion.emisor.imagen,
            "partida_id": notificacion.partida_id if hasattr(notificacion, 'partida_id') else None,
            "tipo": "solicitud_amistad" if notificacion.isinstance(SolicitudAmistad) else "invitacion_partida",
        }
        for notificacion in notificaciones
    ]

def get_solicitud_amistad_by_id(solicitud_id):
    return SolicitudAmistad.objects.filter(id=solicitud_id).first()

def get_solicitud_amistad_by_usuario_ids(emisor_id, receptor_id):
    return SolicitudAmistad.objects.filter(
        emisor_id=emisor_id,
        receptor_id=receptor_id
    ).first()

def get_invitacion_partida_by_usuario_ids(emisor_id, receptor_id):
    return InvitacionPartida.objects.filter(
        emisor_id=emisor_id,
        receptor_id=receptor_id
    ).first()

def get_invitacion_partida_by_id(invitacion_id):
    return InvitacionPartida.objects.filter(id=invitacion_id).first()

def get_invitaciones_de_partida(partida_id):
    return InvitacionPartida.objects.filter(partida_id=partida_id)