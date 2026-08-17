

from ..models.resumen_mano import ResumenMano

from ..selectors.resumen_mano_selector import get_resumen_mano_by_id, get_resumen_mano_by_mano_id

from ..selectors.mano_selector import get_mano_actual

from ..selectors.partida_selector import get_partida_by_id, get_partida_usuario_by_partida_and_usuario


def get_resumen_ult_mano(actor, partida_id):
    """
    Metodo para obtener el resumen de la última mano
    """

    partida_usuario = get_partida_usuario_by_partida_and_usuario(partida_id, actor.id)
    if not partida_usuario:
        raise PermissionError("No participas en la partida.")

    partida = get_partida_by_id(partida_id)
    if not partida:
        raise ValueError("La partida no existe")

    mano_actual = get_mano_actual(partida_id)
    resumen_mano = get_resumen_mano_by_mano_id(mano_actual.id)

    resumen_mano

def create_resumen_mano(partida_id):

    mano_actual = get_mano_actual(partida_id)
    ResumenMano.objects.create(
        mano=mano_actual.id,
        tickets_usados={0:[], 1:[], 2:[], 3:[]},
        victorias={},
        muertes={},
        retiradas={1:[], 2:[], 3:[]},
        efectos_inmediatos_ronda={1:[], 2:[], 3:[]},
        efectos_extra_fin_mano=[]
    )

def recopilar_ticket_usado(resumen_id, ronda_num, color, ticket):

    resumen_mano = get_resumen_mano_by_id(resumen_id)
    resumen_mano.tickets_usados[ronda_num].append((color, ticket))
    resumen_mano.save(update_fields=["tickets_usados"])

def recopilar_victoria(resumen_id, color, tipo_victoria, ronda_num):

    resumen_mano = get_resumen_mano_by_id(resumen_id)
    resumen_mano.victorias[ronda_num] = (color, tipo_victoria)
    resumen_mano.save(update_fields=["victorias"])

def recopilar_muerte(resumen_id, ronda_num, color_matador, color_matado):

    resumen_mano = get_resumen_mano_by_id(resumen_id)
    resumen_mano.muertes[ronda_num] = (color_matador, color_matado)
    resumen_mano.save(update_fields=["muertes"])

def recopilar_retirada(resumen_id, ronda_num, color_retirado):

    resumen_mano = get_resumen_mano_by_id(resumen_id)
    resumen_mano.retiradas[ronda_num].append(color_retirado)
    resumen_mano.save(update_fields=["retiradas"])

def recopilar_efecto_inmediato_ronda(resumen_id, ronda_num, color_beneficiado, efecto):

    resumen_mano = get_resumen_mano_by_id(resumen_id)
    resumen_mano.efectos_inmediatos_ronda[ronda_num].append((color_beneficiado, efecto))
    resumen_mano.save(update_fields=["efectos_inmediatos_ronda"])

def recopilar_efecto_extra_fin_mano(resumen_id, ronda_num, color_beneficiado, efecto):

    resumen_mano = get_resumen_mano_by_id(resumen_id)
    resumen_mano.efectos_extra_fin_mano[ronda_num].append((color_beneficiado, efecto))
    resumen_mano.save(update_fields=["efectos_extra_fin_mano"])
