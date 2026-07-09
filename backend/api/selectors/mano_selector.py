from ..models.partida_usuario import PartidaUsuario
from ..models.mano import Mano

def get_jugadores_en_mesa(id, orden_mesa):
    """
    Obtiene los PUs de los jugadores de la mesa, ordenados tal y como están ordenados los turnos en la mano.
    """
    partida_usuarios = PartidaUsuario.objects.filter(partida=id)

    indice = {color: i for i, color in enumerate(orden_mesa)}

    return sorted(partida_usuarios, key=lambda pu: indice[pu.color])

def get_mano_actual(partida_id):
    """
    Obtiene la mano actual de una partida.
    """
    return Mano.objects.filter(partida_id=partida_id).order_by('-num').first()