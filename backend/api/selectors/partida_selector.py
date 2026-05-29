from ..models.partida import Partida
from ..models.partida_usuario import PartidaUsuario

def get_partidas_publicas_count():
    return Partida.objects.filter(publica=True, fecha_creacion__isnull=False, fecha_inicio__isnull=True).count()

def get_partidas_publicas_paginated(offset, limit):
    return Partida.objects.filter(publica=True, fecha_creacion__isnull=False, fecha_inicio__isnull=True).order_by("id")[offset:offset+limit]

def get_jugadores_actuales_de_partida(id):
    partidaUsuarios = PartidaUsuario.objects.filter(partida=id)
    if not partidaUsuarios:
        return 0
    return partidaUsuarios.count()

def get_estado_de_partida(id):
    partida = Partida.objects.filter(id=id).first()
    if not partida:
        return None
    if partida.fecha_inicio is not None:
        return "en_juego"
    elif partida.fecha_creacion is not None:
        return "sala_espera"
    else:
        return "desconocido"