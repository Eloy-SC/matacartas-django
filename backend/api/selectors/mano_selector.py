from ..models.partida_usuario import PartidaUsuario
from ..models.mano import Mano

def get_jugadores_en_mesa(id, orden_mesa):
    """
    Obtiene los PUs de los jugadores de la mesa, ordenados tal y como están ordenados los turnos en la mano.
    """
    partida_usuarios = PartidaUsuario.objects.filter(partida=id)
    # Build an index mapping colors to order; if a player's color is not in the
    # provided `orden_mesa`, treat it as last to avoid KeyError in tests.
    indice = {color: i for i, color in enumerate(orden_mesa or [])}

    def sort_key(pu):
        try:
            return indice[pu.color]
        except Exception:
            # If color missing or empty, push to the end
            return len(indice)

    return sorted(partida_usuarios, key=sort_key)

def get_mano_actual(partida_id):
    """
    Obtiene la mano actual de una partida.
    """
    return Mano.objects.filter(partida_id=partida_id).order_by('-num').first()