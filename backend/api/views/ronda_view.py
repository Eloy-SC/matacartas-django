from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ..services import ronda_service, mano_service, partida_service
from ..selectors.mano_selector import get_mano_actual
from ..selectors.partida_selector import get_partida_by_id

from ..utils.web_sockets import notificar_mano_finalizada, notificar_mesa_actualizada, notificar_finalizacion_partida


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
    
    if fin_mano:
        mano_actual = get_mano_actual(partida_id)
        partida = get_partida_by_id(partida_id).first()
        notificar_mano_finalizada(partida_id, mano_actual.id)

        if mano_actual.num >= partida.get_num_manos():
            datos_final_partida = partida_service.finalizar_partida(request.user, partida_id)
            notificar_finalizacion_partida(partida_id, datos_final_partida)
        else:
            try:
                mano_service.siguiente_mano(request.user, partida_id)
            except ValueError:
                # Otra petición concurrente ya avanzó la mano.
                pass
            notificar_mesa_actualizada(partida_id)
    else:
        notificar_mesa_actualizada(partida_id)

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
    
    if fin_mano:
        mano_actual = get_mano_actual(partida_id)
        partida = get_partida_by_id(partida_id).first()
        notificar_mano_finalizada(partida_id, mano_actual.id)

        if mano_actual.num >= partida.get_num_manos():
            datos_final_partida = partida_service.finalizar_partida(request.user, partida_id)
            notificar_finalizacion_partida(partida_id, datos_final_partida)
        else:
            try:
                mano_service.siguiente_mano(request.user, partida_id)
            except ValueError:
                # Otra petición concurrente ya avanzó la mano.
                pass
            notificar_mesa_actualizada(partida_id)
    else:
        notificar_mesa_actualizada(partida_id)

    return Response({"detail": "Retirada de la mano realizada correctamente."}, status=200)