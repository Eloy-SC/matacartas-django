from django.db import models

from backend.api.models.notificacion import InvitacionPartida
from ..models import Amistad
from ..models import Usuario

def _amistades_de_usuario(usuario_id, search=None):
    amistades = Amistad.objects.filter(
        models.Q(usuario1_id=usuario_id) | models.Q(usuario2_id=usuario_id)
    )
    if search:
        amistades = amistades.filter(
            models.Q(usuario1_id=usuario_id, usuario2__nombre__icontains=search)
            | models.Q(usuario2_id=usuario_id, usuario1__nombre__icontains=search)
        )
    return amistades

def _usuarios_disponibles_amistad(usuario_id, search=None):
    # Obtener los IDs de los amigos del usuario
    amigos_ids = Amistad.objects.filter(
        models.Q(usuario1_id=usuario_id) | models.Q(usuario2_id=usuario_id)
    ).values_list("usuario1_id", "usuario2_id")

    # Aplanar la lista de tuplas y eliminar el ID del usuario actual
    amigos_ids = set([id for tupla in amigos_ids for id in tupla if id != usuario_id])

    # Filtrar los usuarios que no son amigos y no son el usuario actual
    usuarios_disponibles = Usuario.objects.exclude(id__in=amigos_ids).exclude(id=usuario_id)

    if search:
        usuarios_disponibles = usuarios_disponibles.filter(nombre__icontains=search)

    return usuarios_disponibles

def count_usuarios_disponibles_amistad(usuario_id, search=None):
    return _usuarios_disponibles_amistad(usuario_id, search).count()

def list_usuarios_disponibles_amistad_paginated(usuario_id, offset, limit, search=None):
    usuarios_disponibles = _usuarios_disponibles_amistad(usuario_id, search)[offset:offset + limit]
    return [
        {
            "id": usuario.id,
            "nombre": usuario.nombre,
            "imagen": usuario.imagen,
        }
        for usuario in usuarios_disponibles
    ]

def count_amigos(usuario_id, search=None):
    return _amistades_de_usuario(usuario_id, search).count()

def list_amigos_paginated(usuario_id, offset, limit, search=None):
    amistades = _amistades_de_usuario(usuario_id, search)[offset:offset + limit]
    amigos = [
        amistad.usuario2 if amistad.usuario1_id == usuario_id else amistad.usuario1
        for amistad in amistades
    ]
    res = []
    for amigo in amigos:
        res.append({
            "id": amigo.id,
            "nombre": amigo.nombre,
            "imagen": amigo.imagen,
            "invitado": _get_amigo_invitado(usuario_id, amigo.id)
        })
    return res

def _get_amigo_invitado(usuario_id, amigo_id):
    invitacion = InvitacionPartida.objects.filter(
        emisor_id=usuario_id,
        receptor_id=amigo_id
    ).first()
    if invitacion:
        return True
    else:
        return False

def get_amistad_by_usuario_ids(usuario1_id, usuario2_id):
    """Devuelve la amistad entre dos usuarios, si existe."""
    return Amistad.objects.filter(
        models.Q(usuario1_id=usuario1_id, usuario2_id=usuario2_id)
        | models.Q(usuario1_id=usuario2_id, usuario2_id=usuario1_id)
    ).first()