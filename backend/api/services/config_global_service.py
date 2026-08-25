

from ..selectors.rango_selector import get_rango_by_id

from ..models.configuracion_global import ConfiguracionGlobal


def obtener_rango_minimo_crear_torneo(actor):
    """
    Devuelve el rango mínimo requerido para crear torneos.
    """
    if not actor.is_active:
        raise PermissionError("No tienes permiso para obtener el rango")
    
    config_global = ConfiguracionGlobal.objects.get(pk=1)

    rango_id = config_global.rango_minimo_crear_torneo_id
    rango = get_rango_by_id(rango_id)
    return rango

def cambiar_rango_minimo_crear_torneo(actor, rango_id, no_rango=False):
    """
    Permite establecer el rango minimo requerido para crear torneos. Solo los administradores pueden realizar esta acción.
    """

    config_global = ConfiguracionGlobal.objects.get(pk=1)

    if not actor.is_staff:
        raise PermissionError("No tienes permisos para cambiar el rango mínimo para crear torneos.")

    if no_rango:
        config_global.rango_minimo_crear_torneo = None
    else:
        rango = get_rango_by_id(rango_id)
        if rango is None:
            raise ValueError("El rango especificado no existe.")
        config_global.rango_minimo_crear_torneo = rango
    config_global.save(update_fields=["rango_minimo_crear_torneo"])
    