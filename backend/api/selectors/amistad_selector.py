from django.db import models
from ..models import Amistad


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


def list_amigos(usuario_id, search=None):
    """Devuelve los amigos del usuario, filtrados opcionalmente por nombre."""
    amistades = _amistades_de_usuario(usuario_id, search)
    amigos = []
    for amistad in amistades:
        if amistad.usuario1_id == usuario_id:
            amigos.append(amistad.usuario2)
        else:
            amigos.append(amistad.usuario1)
    return amigos


def count_amigos(usuario_id, search=None):
    return _amistades_de_usuario(usuario_id, search).count()


def list_amigos_paginated(usuario_id, offset, limit, search=None):
    amistades = _amistades_de_usuario(usuario_id, search)[offset:offset + limit]
    return [
        amistad.usuario2 if amistad.usuario1_id == usuario_id else amistad.usuario1
        for amistad in amistades
    ]