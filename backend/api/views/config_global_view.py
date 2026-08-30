from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from ..services import config_global_service


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def obtener_rango_minimo_crear_torneo(request):
    """
    Devuelve el rango mínimo para crear torneos.
    """
    try:
        rango_minimo = config_global_service.obtener_rango_minimo_crear_torneo(request.user)
    except PermissionError as e:
        return Response({"detail": str(e)}, status=403)

    if rango_minimo is None:
        data = {
            "id": None,
            "nombre": "Sin rango",
            "color": "blanco",
            "puntos_minimos": None,
            "puntos_maximos": None,
        }
    else:
        data = {
            "id": rango_minimo.id,
            "nombre": rango_minimo.nombre,
            "color": rango_minimo.color,
            "puntos_minimos": rango_minimo.puntos_minimos,
            "puntos_maximos": rango_minimo.puntos_maximos,
        }

    return Response(data, status=200)

@api_view(["PUT"])
@permission_classes([IsAdminUser])
def cambiar_rango_minimo_crear_torneo(request):
    try:
        rango_id = request.data.get("rango_id")
        if rango_id is not None:
            config_global_service.cambiar_rango_minimo_crear_torneo(request.user, rango_id)
        else:
            config_global_service.cambiar_rango_minimo_crear_torneo(request.user, rango_id, True)
    except PermissionError as e:
        return Response({"detail": str(e)}, status=403)
    except ValueError as e:
        return Response({"detail": str(e)}, status=404)

    return Response({"detail": "Rango mínimo para crear torneos cambiado correctamente."}, status=200)