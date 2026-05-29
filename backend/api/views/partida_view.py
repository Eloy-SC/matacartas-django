from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from ..services import partida_service

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def listar_partidas_publicas(request):
    page_param = request.query_params.get("page", "1")
    try:
        page = max(1, int(page_param))
    except (TypeError, ValueError):
        page = 1
    page_size = 10

    try:
        paged = partida_service.listar_partidas_publicas(
            request.user,
            page=page,
            page_size=page_size,
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
