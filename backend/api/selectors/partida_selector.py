from ..models.usuario import Usuario
from ..models.partida import Partida
from ..models.partida_usuario import PartidaUsuario
from django.db.models import Q

def _build_partidas_queryset(search=None, nombre=None, num_jugadores=None, rango_minimo_id=None, rango_maximo_id=None, empezada=None):
    queryset = Partida.objects.filter(privada=False, fecha_creacion__isnull=False, fecha_fin__isnull=True)

    if search:
        search = search.strip()
        if search:
            search_filters = Q(nombre__icontains=search)
            if search.isdigit():
                search_filters |= Q(id=int(search))
            queryset = queryset.filter(search_filters)

    if nombre:
        nombre = nombre.strip()
        if nombre:
            queryset = queryset.filter(nombre__icontains=nombre)

    if num_jugadores is not None:
        queryset = queryset.filter(num_jugadores=num_jugadores)

    if rango_minimo_id is not None:
        queryset = queryset.filter(rango_minimo_id=rango_minimo_id)

    if rango_maximo_id is not None:
        queryset = queryset.filter(rango_maximo_id=rango_maximo_id)
    
    if empezada is not None:
        queryset = queryset.filter(fecha_inicio__isnull=False) if empezada else queryset.filter(fecha_inicio__isnull=True)

    return queryset

def get_partidas_publicas_paginated(
        offset, 
        limit,
        *,
        search=None,
        nombre=None,
        num_jugadores=None,
        rango_minimo_id=None,
        rango_maximo_id=None,
        empezada=None,
        ordering=None,
):
    queryset = _build_partidas_queryset(
        search=search,
        nombre=nombre,
        num_jugadores=num_jugadores,
        rango_minimo_id=rango_minimo_id,
        rango_maximo_id=rango_maximo_id,
        empezada=empezada,
    )

    order_fields = []
    if ordering:
        order_fields.append(ordering)
        if ordering.lstrip("-") != "id":
            order_fields.append("id")
    else:
        order_fields.append("id")
    
    return queryset.values("id",
                            "nombre", 
                            "num_jugadores", 
                            "rango_minimo_id", 
                            "rango_maximo_id", 
                            "fecha_creacion", 
                            "fecha_inicio", 
                            "fecha_fin").order_by(*order_fields)[offset:offset+limit]

def get_partidas_publicas_count(*, search=None, nombre=None, num_jugadores=None, rango_minimo_id=None, rango_maximo_id=None, empezada=None):
    queryset = _build_partidas_queryset(
        search=search,
        nombre=nombre,
        num_jugadores=num_jugadores,
        rango_minimo_id=rango_minimo_id,
        rango_maximo_id=rango_maximo_id,
        empezada=empezada,
    )
    return queryset.count()

def get_jugadores_actuales_de_partida_count(id):
    partidaUsuarios = PartidaUsuario.objects.filter(partida=id)
    if not partidaUsuarios:
        return 0
    return partidaUsuarios.count()

def get_jugadores_actuales_de_partida(id):
    partidaUsuarios = PartidaUsuario.objects.filter(partida=id).select_related('usuario')
    if not partidaUsuarios:
        return []
    
    jugadores = []
    for pu in partidaUsuarios:
        jugadores.append({
            'id': pu.usuario.id,
            'username': pu.usuario.username,
            'nombre': pu.usuario.nombre,
            'email': pu.usuario.email,
            'imagen': pu.usuario.imagen,
            'puntuacion': pu.usuario.puntuacion,
            'listo': pu.listo
        })
    return jugadores

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

def get_partida_by_id(id):
    return Partida.objects.filter(id=id)

def get_partida_by_nombre(nombre):
    return Partida.objects.filter(nombre=nombre)

def get_partida_by_clave(clave):
    return Partida.objects.filter(clave=clave)

def get_jugador_participa_en_partida(partida_id, usuario_id):
    return PartidaUsuario.objects.filter(partida_id=partida_id, usuario_id=usuario_id).exists()

def get_partida_usuario_by_partida_and_usuario(partida_id, usuario_id):
    return PartidaUsuario.objects.filter(partida_id=partida_id, usuario_id=usuario_id).first()
    