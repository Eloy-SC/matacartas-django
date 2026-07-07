from ..services import mano_service
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def repartir_cartas(request, partida_id):
    """
    Endpoint para repartir cartas a los jugadores de una partida.
    """
    try:
        mano_service.repartir_cartas(request.user, partida_id)
    except PermissionError as e:
        return Response({"detail": str(e)}, status=403)
    except ValueError as e:
        return Response({"detail": str(e)}, status=404)
    
    return Response({"detail": "Cartas repartidas correctamente."}, status=200)