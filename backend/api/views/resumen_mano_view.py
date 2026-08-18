from ..services import resumen_mano_service
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_resumen_ult_mano(request, partida_id):
    """
    Endpoint para obtener la información del fin de la mano
    """
    try:
        mano_resumen = resumen_mano_service.get_resumen_ult_mano(request.user, partida_id)
    except PermissionError as e:
        return Response({"detail": str(e)}, status=403)
    except ValueError as e:
        return Response({"detail": str(e)}, status=404)

    return Response(
        {
            "mano_id": mano_resumen.mano_id,
            "tickets_usados": mano_resumen.tickets_usados,
            "victorias": mano_resumen.victorias,
            "muertes": mano_resumen.muertes,
            "retiradas": mano_resumen.retiradas,
            "efectos_inmediatos_ronda": mano_resumen.efectos_inmediatos_ronda,
            "efectos_extra_fin_mano": mano_resumen.efectos_extra_fin_mano,
        },
        status=200,
    )