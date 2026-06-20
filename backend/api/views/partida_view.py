from ..serializers.partida_serializer import CrearPartidaSerializer
from ..utils.exceptions import RegistrationError
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from ..services import partida_service
from ..utils.web_sockets import notificar_sala_actualizada

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
def listar_partidas_publicas(request):
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
    num_jugadores = request.query_params.get("num_jugadores")
    if num_jugadores is not None:
        try:
            num_jugadores = int(num_jugadores)
            if num_jugadores <= 0:
                num_jugadores = None
        except (TypeError, ValueError):
            num_jugadores = None
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
    empezada = _parse_bool_param(request.query_params.get("empezada"))
    
    ordering_param = (request.query_params.get("ordering") or "id").strip()
    order_dir = "asc"
    order_by = ordering_param
    if ordering_param.startswith("-"):
        order_dir = "desc"
        order_by = ordering_param[1:] or "id"

    try:
        paged = partida_service.listar_partidas_publicas(
            request.user,
            page=page,
            page_size=page_size,
            search=search,
            nombre = nombre,
            num_jugadores = num_jugadores,
            rango_minimo_id = rango_minimo_id,
            rango_maximo_id = rango_maximo_id,
            empezada = empezada,
            order_by=order_by,
            order_dir=order_dir,
        )
    except PermissionError as e:
        return Response({"detail": str(e)}, status=403)
    
    data = [
        {
            "id": partida["id"],
            "nombre": partida["nombre"],
            "jugadores_maximos": partida["jugadores_maximos"],
            "rango_minimo": partida["rango_minimo"],
            "rango_maximo": partida["rango_maximo"],
            "jugadores_actuales": partida["jugadores_actuales"],
            "estado": partida["estado"],
        }
        for partida in paged["items"]
    ]

    return Response(
        {
            "items": data,
            "page": paged["page"],
            "page_size": paged["page_size"],
            "total": paged["total"],
            "total_pages": paged["total_pages"],
        },
        status=200,
    )

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def crear_partida(request):
    serializer = CrearPartidaSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=400)
    
    try:
        partida = partida_service.crear_partida(
            actor=request.user,
            nombre=serializer.validated_data["nombre"],
            num_jugadores=serializer.validated_data["num_jugadores"],
            privada=serializer.validated_data["privada"],
            clave=serializer.validated_data["clave"],
            longitud=serializer.validated_data["longitud"],
            cartas_invencibles=serializer.validated_data["cartas_invencibles"],
            tiempo_max_turno=serializer.validated_data["tiempo_max_turno"],
            rango_minimo_id=serializer.validated_data["rango_minimo_id"],
            rango_maximo_id=serializer.validated_data["rango_maximo_id"],
        )
    except PermissionError as e:
        return Response({"detail": str(e)}, status=403)
    except RegistrationError as e:
        return Response(e.errors, status=400)
    except ValueError as e:
        return Response({"detail": str(e)}, status=404)
    
    return Response(
        {
            "id": partida.id,
            "nombre": partida.nombre,
            "num_jugadores": partida.num_jugadores,
            "privada": partida.privada,
            "clave": partida.clave,
            "longitud": partida.longitud,
            "cartas_invencibles": partida.cartas_invencibles,
            "tiempo_max_turno": partida.tiempo_max_turno,
            "rango_minimo_id": partida.rango_minimo.id if partida.rango_minimo else None,
            "rango_maximo_id": partida.rango_maximo.id if partida.rango_maximo else None,
        },
        status=status.HTTP_201_CREATED,
    )

@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def editar_partida(request, partida_id):
    serializer = CrearPartidaSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=400)
    
    try:
        partida = partida_service.editar_partida(
            actor=request.user,
            partida_id=partida_id,
            nombre=serializer.validated_data["nombre"],
            num_jugadores=serializer.validated_data["num_jugadores"],
            privada=serializer.validated_data["privada"],
            clave=serializer.validated_data["clave"],
            longitud=serializer.validated_data["longitud"],
            cartas_invencibles=serializer.validated_data["cartas_invencibles"],
            tiempo_max_turno=serializer.validated_data["tiempo_max_turno"],
            rango_minimo_id=serializer.validated_data["rango_minimo_id"],
            rango_maximo_id=serializer.validated_data["rango_maximo_id"],
        )
    except PermissionError as e:
        return Response({"detail": str(e)}, status=403)
    except RegistrationError as e:
        return Response(e.errors, status=400)
    except ValueError as e:
        return Response({"detail": str(e)}, status=404)
    
    return Response(
        {
            "id": partida.id,
            "nombre": partida.nombre,
            "num_jugadores": partida.num_jugadores,
            "privada": partida.privada,
            "clave": partida.clave,
            "longitud": partida.longitud,
            "cartas_invencibles": partida.cartas_invencibles,
            "tiempo_max_turno": partida.tiempo_max_turno,
            "rango_minimo_id": partida.rango_minimo.id if partida.rango_minimo else None,
            "rango_maximo_id": partida.rango_maximo.id if partida.rango_maximo else None,
        },
        status=status.HTTP_200_OK,
    )

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_partida_como_jugador(request, partida_id):
    try:
        partida = partida_service.get_partida_como_jugador(request.user, partida_id)
    except PermissionError as e:
        return Response({"detail": str(e)}, status=403)
    except ValueError as e:
        return Response({"detail": str(e)}, status=404)
    
    data = {
        "id": partida.id,
        "nombre": partida.nombre,
        "num_jugadores": partida.num_jugadores,
        "privada": partida.privada,
        "clave": partida.clave,
        "longitud": partida.longitud,
        "cartas_invencibles": partida.cartas_invencibles,
        "tiempo_max_turno": partida.tiempo_max_turno,
        "rango_minimo_id": partida.rango_minimo.id if partida.rango_minimo else None,
        "rango_maximo_id": partida.rango_maximo.id if partida.rango_maximo else None,
    }

    return Response(data, status=200)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_jugadores_partida(request, partida_id):
    try:
        jugadores = partida_service.get_jugadores_partida(request.user, partida_id)
    except PermissionError as e:
        return Response({"detail": str(e)}, status=403)
    except ValueError as e:
        return Response({"detail": str(e)}, status=404)
    
    data = [
        {
            "id": jugador["id"],
            "nombre": jugador["nombre"],
            "imagen": jugador["imagen"],
            "creador": jugador["creador"],
            "listo": jugador["listo"],
        }
        for jugador in jugadores
    ]

    return Response(data, status=200)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_jugador_participa_en_partida(request, partida_id):
    try:
        jugadores = partida_service.get_jugadores_partida(request.user, partida_id)
    except PermissionError as e:
        return Response({"detail": str(e)}, status=403)
    except ValueError as e:
        return Response({"detail": str(e)}, status=404)
    
    if request.user.id in [jugador["id"] for jugador in jugadores]:
        participa = True
    else:
        participa = False

    return Response({"participa": participa}, status=200)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_jugador_participa_en_partida_privada(request, clave):
    try:
        partida = partida_service.get_partida_by_clave(clave).first()
        jugadores = partida_service.get_jugadores_partida(request.user, partida.id)
    except PermissionError as e:
        return Response({"detail": str(e)}, status=403)
    except ValueError as e:
        return Response({"detail": str(e)}, status=404)
    
    if request.user.id in [jugador["id"] for jugador in jugadores]:
        participa = True
    else:
        participa = False

    return Response({"participa": participa, "id": partida.id}, status=200)

@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def abandonar_partida(request, partida_id):
    try:
        partida_service.abandonar_partida(request.user, partida_id)
    except PermissionError as e:
        return Response({"detail": str(e)}, status=403)
    except ValueError as e:
        return Response({"detail": str(e)}, status=404)
    
    notificar_sala_actualizada(partida_id)
    
    return Response({"detail": "Abandonada la partida correctamente."}, status=200)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def unirse_a_partida_publica(request, partida_id):
    try:
        partida_service.unirse_a_partida_publica(request.user, partida_id)
    except PermissionError as e:
        return Response({"detail": str(e)}, status=403)
    except ValueError as e:
        return Response({"detail": str(e)}, status=404)
    
    notificar_sala_actualizada(partida_id)
    
    return Response({"detail": "Unido a la partida correctamente."}, status=200)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def unirse_a_partida_privada(request, clave):
    try:
        partida_service.unirse_a_partida_privada(request.user, clave)
    except PermissionError as e:
        return Response({"detail": str(e)}, status=403)
    except ValueError as e:
        return Response({"detail": str(e)}, status=404)
    
    partida_id = partida_service.get_partida_by_clave(clave).first().id
    notificar_sala_actualizada(partida_id)
    
    return Response({"detail": "Unido a la partida correctamente."}, status=200)

@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def toggle_listo(request, partida_id):
    try:
        partida_service.toggle_listo(request.user, partida_id)
    except PermissionError as e:
        return Response({"detail": str(e)}, status=403)
    except ValueError as e:
        return Response({"detail": str(e)}, status=404)
    
    notificar_sala_actualizada(partida_id)

    return Response({"detail": "Estado listo cambiado correctamente."}, status=200)

@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def expulsar_jugador(request, partida_id, jugador_id):
    try:
        partida_service.expulsar_jugador(request.user, partida_id, jugador_id)
    except PermissionError as e:
        return Response({"detail": str(e)}, status=403)
    except ValueError as e:
        return Response({"detail": str(e)}, status=404)
    
    notificar_sala_actualizada(partida_id)

    return Response({"detail": "Jugador expulsado correctamente."}, status=200)