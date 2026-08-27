from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ..serializers.torneo_serializer import TorneoSerializer
from ..services import torneo_service
from ..utils.exceptions import RegistrationError


def _parse_bool_param(value):
    if value is None:
        return None
    normalized = str(value).strip().lower()
    if normalized in {"true", "1", "yes", "si", "y"}:
        return True
    if normalized in {"false", "0", "no", "n"}:
        return False
    return None


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def listar_torneos_publicos(request):
    page_param = request.query_params.get("page", "1")
    try:
        page = max(1, int(page_param))
    except (TypeError, ValueError):
        page = 1
    page_size = 10

    search = (request.query_params.get("search") or "").strip()
    if not search:
        search = None

    nombre = (request.query_params.get("nombre") or "").strip()
    if not nombre:
        nombre = None

    rango_minimo_id = request.query_params.get("rango_minimo_id")
    if rango_minimo_id is not None:
        try:
            rango_minimo_id = int(rango_minimo_id)
            if rango_minimo_id <= 0:
                rango_minimo_id = None
        except (TypeError, ValueError):
            rango_minimo_id = None

    rango_maximo_id = request.query_params.get("rango_maximo_id")
    if rango_maximo_id is not None:
        try:
            rango_maximo_id = int(rango_maximo_id)
            if rango_maximo_id <= 0:
                rango_maximo_id = None
        except (TypeError, ValueError):
            rango_maximo_id = None

    empezado = _parse_bool_param(request.query_params.get("empezado"))

    ordering_param = (request.query_params.get("ordering") or "id").strip()
    order_dir = "asc"
    order_by = ordering_param
    if ordering_param.startswith("-"):
        order_dir = "desc"
        order_by = ordering_param[1:] or "id"

    try:
        paged = torneo_service.listar_torneos_publicos(
            request.user,
            page=page,
            page_size=page_size,
            search=search,
            nombre=nombre,
            rango_minimo_id=rango_minimo_id,
            rango_maximo_id=rango_maximo_id,
            empezado=empezado,
            order_by=order_by,
            order_dir=order_dir,
        )
    except PermissionError as e:
        return Response({"detail": str(e)}, status=403)

    return Response(
        {
            "items": paged["items"],
            "page": paged["page"],
            "page_size": paged["page_size"],
            "total": paged["total"],
            "total_pages": paged["total_pages"],
        },
        status=200,
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def crear_torneo(request):
    serializer = TorneoSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=400)

    try:
        torneo = torneo_service.crear_torneo(request.user, **serializer.validated_data)
    except PermissionError as e:
        return Response({"detail": str(e)}, status=403)
    except RegistrationError as e:
        return Response(e.errors, status=400)
    except ValueError as e:
        return Response({"detail": str(e)}, status=400)

    return Response(
        {
            "id": torneo.id,
            "nombre": torneo.nombre,
            "detail": "Torneo creado",
        },
        status=status.HTTP_201_CREATED,
    )

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_torneo(request, torneo_id):
    try:
        torneo = torneo_service.get_torneo(request.user, torneo_id)
    except PermissionError as e:
        return Response({"detail": str(e)}, status=403)
    except ValueError as e:
        return Response({"detail": str(e)}, status=404)

    data = {
        "id": torneo.id,
        "nombre": torneo.nombre,
        "fecha_creacion": torneo.fecha_creacion,
        "fecha_inicio": torneo.fecha_inicio,
        "fecha_fin": torneo.fecha_fin,
        "rango_minimo_id": torneo.rango_minimo.id if torneo.rango_minimo else None,
        "rango_maximo_id": torneo.rango_maximo.id if torneo.rango_maximo else None,
        "num_jug_fin": torneo.num_jug_fin,
        "num_jug_sem": torneo.num_jug_sem,
        "num_jug_cua": torneo.num_jug_cua,
        "num_jug_oct": torneo.num_jug_oct,
        "partidas_longitud": torneo.partidas_longitud,
        "partidas_cartas_especiales": torneo.partidas_cartas_especiales,
        "partidas_tickets": torneo.partidas_tickets,
        "partidas_tiempo_max_turno": torneo.partidas_tiempo_max_turno,
        "desempate_mayor_punt": torneo.desempate_mayor_punt,
    }

    return Response(data, status=200)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_participantes_torneo(request, torneo_id):
    try:
        participantes = torneo_service.get_participantes_torneo(request.user, torneo_id)
    except PermissionError as e:
        return Response({"detail": str(e)}, status=403)
    except ValueError as e:
        return Response({"detail": str(e)}, status=404)

    data = [
        {
            "id": participante["id"],
            "nombre": participante["nombre"],
            "imagen": participante["imagen"],
            "creador": participante["creador"],
            "eliminado": participante["eliminado"]
        }
        for participante in participantes
    ]

    return Response(data, status=200)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def unirse_a_torneo(request, torneo_id):
    try:
        torneo_service.unirse_a_torneo(request.user, torneo_id)
    except PermissionError as e:
        return Response({"detail": str(e)}, status=403)
    except ValueError as e:
        return Response({"detail": str(e)}, status=404)

    return Response({"detail": "Usuario unido al torneo"}, status=200)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_partida_pertenece_a_torneo(request, partida_id):
    try:
        partida_torneo = torneo_service.get_partida_pertenece_a_torneo(request.user, partida_id)
    except PermissionError as e:
        return Response({"detail": str(e)}, status=403)
    except ValueError as e:
        return Response({"detail": str(e)}, status=404)
    
    if partida_torneo is not None:
        pertenece_a_torneo = True
    else:
        pertenece_a_torneo = False

    return Response({"pertenece_a_torneo": pertenece_a_torneo}, status=200)