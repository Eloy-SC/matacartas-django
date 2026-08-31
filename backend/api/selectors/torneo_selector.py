from django.db.models import Q
from django.contrib.auth import get_user_model

from ..models.partida_usuario import PartidaUsuario

from ..models.partida_torneo import PartidaTorneo

from ..models.torneo_usuario import TorneoUsuario

from ..models.torneo import Torneo


def _build_torneos_queryset(search=None, nombre=None, rango_minimo_id=None, rango_maximo_id=None, empezado=None):
    queryset = Torneo.objects.all()

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

    if rango_minimo_id is not None:
        queryset = queryset.filter(rango_minimo_id=rango_minimo_id)

    if rango_maximo_id is not None:
        queryset = queryset.filter(rango_maximo_id=rango_maximo_id)

    if empezado is not None:
        queryset = queryset.filter(fecha_inicio__isnull=False) if empezado else queryset.filter(fecha_inicio__isnull=True)

    return queryset


def get_torneos_publicos_paginated(
    offset,
    limit,
    *,
    search=None,
    nombre=None,
    rango_minimo_id=None,
    rango_maximo_id=None,
    empezado=None,
    ordering=None,
):
    queryset = _build_torneos_queryset(
        search=search,
        nombre=nombre,
        rango_minimo_id=rango_minimo_id,
        rango_maximo_id=rango_maximo_id,
        empezado=empezado,
    )

    order_fields = []
    if ordering:
        order_fields.append(ordering)
        if ordering.lstrip("-") != "id":
            order_fields.append("id")
    else:
        order_fields.append("id")

    return queryset.values(
        "id",
        "nombre",
        "rango_minimo_id",
        "rango_maximo_id",
        "num_jug_fin",
        "num_jug_sem",
        "num_jug_cua",
        "num_jug_oct",
        "partidas_longitud",
        "partidas_cartas_especiales",
        "partidas_tickets",
        "partidas_tiempo_max_turno",
        "desempate_mayor_punt",
        "fecha_creacion",
        "fecha_inicio",
        "fecha_fin",
    ).order_by(*order_fields)[offset:offset + limit]


def get_torneos_publicos_count(*, search=None, nombre=None, rango_minimo_id=None, rango_maximo_id=None, empezado=None):
    queryset = _build_torneos_queryset(
        search=search,
        nombre=nombre,
        rango_minimo_id=rango_minimo_id,
        rango_maximo_id=rango_maximo_id,
        empezado=empezado,
    )
    return queryset.count()


def get_torneo_by_id(torneo_id):
    return Torneo.objects.filter(id=torneo_id).first()


def get_torneo_by_nombre(nombre):
    return Torneo.objects.filter(nombre=nombre).first()

def get_participantes_torneo_by_torneo_id_count(torneo_id):
    return TorneoUsuario.objects.filter(torneo=torneo_id).count()

def get_participantes_torneo_by_torneo_id(torneo_id):
    torneo_usuarios = TorneoUsuario.objects.filter(torneo=torneo_id).select_related('usuario')
    if not torneo_usuarios:
        return []

    participantes = []
    for pt in torneo_usuarios:
        participantes.append({
            "id": pt.usuario.id,
            "username": pt.usuario.username,
            "nombre": pt.usuario.nombre,
            "imagen": pt.usuario.imagen if pt.usuario.imagen else None,
            "creador": pt.creador,
            "eliminado": pt.eliminado,
        })

    return participantes

def get_partida_torneo_by_partida_id(partida_id):
    partida_torneo = PartidaTorneo.objects.filter(partida__id=partida_id).first()
    return partida_torneo

def get_partidas_torneo_by_fase(torneo_id, fase):
    return PartidaTorneo.objects.filter(torneo__id=torneo_id, fase=fase).order_by('lado', 'pareja').all()

def get_torneo_by_partida(partida_id):
    partida_torneo = get_partida_torneo_by_partida_id(partida_id)
    if partida_torneo:
        return partida_torneo.torneo
    return None

def get_fase_actual_torneo(torneo_id):
    torneo = get_torneo_by_id(torneo_id)
    fases = [PartidaTorneo.FasePartida.SEMIFINAL, PartidaTorneo.FasePartida.FINAL]
    if torneo.num_jug_cua is not None and torneo.num_jug_cua > 0:
        fases.insert(0, PartidaTorneo.FasePartida.CUARTOS)
    if torneo.num_jug_oct is not None and torneo.num_jug_oct > 0:
        fases.insert(0, PartidaTorneo.FasePartida.OCTAVOS)
    for i in range(0, len(fases)):
        if PartidaTorneo.objects.filter(torneo__id=torneo_id, fase=fases[i]).exists():
            continue
        else:
            return fases[i-1] if i > 0 else fases[0]
    return None

def get_torneo_usuario_by_torneo_and_usuario_id(torneo_id, usuario_id):
    return TorneoUsuario.objects.filter(torneo__id=torneo_id, usuario__id=usuario_id).first()

def get_torneo_usuario_by_usuario(usuario_id):
    return TorneoUsuario.objects.filter(usuario__id=usuario_id).first()

def get_partida_actual_de_torneo_by_torneo_and_usuario_id(torneo_id, usuario_id):

    partidas_torneo = PartidaTorneo.objects.filter(torneo__id=torneo_id)
    for pt in partidas_torneo:
        if pt.fase == get_fase_actual_torneo(torneo_id):
            partida_id = pt.partida.id
            partida_usuario = PartidaUsuario.objects.filter(partida__id=partida_id, usuario__id=usuario_id).first()
            if partida_usuario:
                return pt.partida

def get_torneo_usuario_by_usernames(lista_usernames):
    UserModel = get_user_model()
    objs = UserModel.objects.filter(username__in=lista_usernames)
    lista_ids = [user.id for user in objs]
    return TorneoUsuario.objects.filter(usuario__id__in=lista_ids)

def get_partida_final_de_torneo(torneo_id):
    return PartidaTorneo.objects.filter(torneo__id=torneo_id, fase=PartidaTorneo.FasePartida.FINAL).first()

def get_torneo_usuario_by_torneo_id_exclude_usernames(torneo_id, lista_usernames):
    return TorneoUsuario.objects.filter(torneo=torneo_id).exclude(usuario__username__in=lista_usernames)