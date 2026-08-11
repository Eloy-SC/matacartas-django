from ..utils.web_sockets import notificar_mesa_actualizada
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ..services import ticket_service

@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def usar_ticket(request, partida_id):
    """
    Endpoint para usar un ticket en una partida.
    """
    try:
        ticket = request.data.get("ticket")
        if not ticket:
            return Response({"detail": "No se proporcionó el ticket a usar."}, status=400)
        ticket_service.usar_ticket(request.user, partida_id, ticket)
    except PermissionError as e:
        return Response({"detail": str(e)}, status=403)
    except ValueError as e:
        return Response({"detail": str(e)}, status=404)

    notificar_mesa_actualizada(partida_id)

    return Response({"detail": "Ticket usado correctamente."}, status=200)