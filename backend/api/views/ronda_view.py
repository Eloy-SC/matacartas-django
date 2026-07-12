from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ..services import ronda_service

from ..utils.web_sockets import notificar_mesa_actualizada


@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def jugar_carta(request, partida_id):
    """
    Endpoint para jugar una carta en una partida.
    """
    try:
        carta = request.data.get("carta")
        if not carta:
            return Response({"detail": "No se proporcionó la carta a jugar."}, status=400)
        ronda_service.jugar_carta(request.user, partida_id)
    except PermissionError as e:
        return Response({"detail": str(e)}, status=403)
    except ValueError as e:
        return Response({"detail": str(e)}, status=404)
    
    notificar_mesa_actualizada(partida_id)
    
    return Response({"detail": "Carta jugada correctamente."}, status=200)