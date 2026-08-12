from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ..services import ronda_service
from ..selectors.mano_selector import get_mano_actual

from ..utils.web_sockets import notificar_mano_finalizada, notificar_mesa_actualizada


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
        fin_mano = ronda_service.jugar_carta(request.user, partida_id, carta)
    except PermissionError as e:
        return Response({"detail": str(e)}, status=403)
    except ValueError as e:
        return Response({"detail": str(e)}, status=404)
    
    notificar_mesa_actualizada(partida_id)

    if fin_mano:
        notificar_mano_finalizada(partida_id, get_mano_actual(partida_id).id)

    return Response({"detail": "Carta jugada correctamente."}, status=200)

@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def retirarse_de_mano(request, partida_id):
    """
    Endpoint para retirarse de una mano en una partida.
    """
    try:
        fin_mano = ronda_service.retirarse_de_mano(request.user, partida_id)
    except PermissionError as e:
        return Response({"detail": str(e)}, status=403)
    except ValueError as e:
        return Response({"detail": str(e)}, status=404)
    
    notificar_mesa_actualizada(partida_id)

    if fin_mano:
        notificar_mano_finalizada(partida_id, get_mano_actual(partida_id).id)

    return Response({"detail": "Retirada de la mano realizada correctamente."}, status=200)