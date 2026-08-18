from dataclasses import asdict

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
            "mano_num": mano_resumen.mano_num,
            "ronda_prep": asdict(mano_resumen.ronda_prep),
            "ronda_1": asdict(mano_resumen.ronda_1),
            "ronda_2": asdict(mano_resumen.ronda_2),
            "ronda_3": asdict(mano_resumen.ronda_3),
            "ronda_com": asdict(mano_resumen.ronda_com),
            "efectos_extra_fin_mano": mano_resumen.efectos_extra_fin_mano,
            "ganador": mano_resumen.ganador,
        },
        status=200,
    )