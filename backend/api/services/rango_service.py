from django.db import IntegrityError

from backend.api.models import rango
from backend.api.selectors.rango_selector import get_rango_by_max_puntos, get_rango_by_min_puntos, get_rango_by_min_puntos, get_rangos_parejas_valores

from ..models import Rango
from ..utils.exceptions import RegistrationError


def listar_rangos(actor):
	if not actor.is_active:
		raise PermissionError("No tienes permiso para listar rangos")

	return Rango.objects.all().values(
		"id",
		"nombre",
		"color",
		"puntos_minimos",
		"puntos_maximos",
	).order_by("puntos_minimos")


def get_rango(actor, rango_id):
	if not actor.is_active:
		raise PermissionError("No tienes permiso para obtener el rango")

	return (
		Rango.objects.filter(id=rango_id)
		.values("id", "nombre", "color", "puntos_minimos", "puntos_maximos")
		.first()
	)


def crear_rango_admin(actor, *, nombre, color, puntos_minimos, puntos_maximos):
    """
    Crea un nuevo rango con los datos proporcionados. Sólo puede ser utilizado por administradores.
    """
    if not actor.is_staff:
        raise PermissionError("No tienes permiso para crear un rango")

    intervalos = get_rangos_parejas_valores()
    for min_puntos, max_puntos in intervalos:
        if (puntos_minimos >= min_puntos and puntos_minimos <= max_puntos) or \
           (puntos_maximos >= min_puntos and puntos_maximos <= max_puntos) or \
           (puntos_minimos <= min_puntos and puntos_maximos >= max_puntos):
            raise RegistrationError({"detail": "Los puntos mínimos y máximos no pueden solaparse con los de otro rango"})
	
    min_solapado = get_rango_by_max_puntos(puntos_minimos)
    if min_solapado is not None:
        nuevos_puntos_minimos = puntos_minimos + 1
        if get_rango_by_min_puntos(nuevos_puntos_minimos) is not None:
            raise RegistrationError({"detail": "Ya hay un rango con f{puntos_minimos} como máximo y \
									  otro con {nuevos_puntos_minimos} como mínimo"})
    max_solapado = get_rango_by_min_puntos(puntos_maximos)
    if max_solapado is not None:
        nuevos_puntos_maximos = puntos_maximos - 1
        if get_rango_by_min_puntos(nuevos_puntos_maximos) is not None:
            raise RegistrationError({"detail": "Ya hay un rango con f{puntos_maximos} como mínimo y \
									  otro con {nuevos_puntos_maximos} como máximo"})
        
    if nombre == "Sin rango":
        raise RegistrationError({"detail": "No se puede crear un rango con el nombre \"Sin rango\""})
    
    rango = Rango(
		nombre=nombre,
		color=color,
		puntos_minimos=puntos_minimos,
		puntos_maximos=puntos_maximos,
	)

    try:
        rango.save()
    except IntegrityError as e:
        msg = str(e)
        if "nombre" in msg:
            raise RegistrationError({"nombre": ["El nombre ya existe"]})
        if "puntos_minimos" in msg:
            raise RegistrationError({"puntos_minimos": ["Los puntos minimos ya existen"]})
        if "puntos_maximos" in msg:
            raise RegistrationError({"puntos_maximos": ["Los puntos maximos ya existen"]})
        raise RegistrationError({"detail": ["No se pudo crear el rango"]})

    return rango


def editar_rango_admin(actor, rango_id, *, nombre, color, puntos_minimos, puntos_maximos):
    """
    Edita un rango por su ID. Sólo puede ser utilizado por administradores.
    """
    if not actor.is_staff:
        raise PermissionError("No tienes permiso para editar un rango")
    
    intervalos = get_rangos_parejas_valores()
    for min_puntos, max_puntos in intervalos:
        if (puntos_minimos >= min_puntos and puntos_minimos <= max_puntos) or \
           (puntos_maximos >= min_puntos and puntos_maximos <= max_puntos) or \
           (puntos_minimos <= min_puntos and puntos_maximos >= max_puntos):
            raise RegistrationError({"detail": "Los puntos mínimos y máximos no pueden solaparse con los de otro rango"})
	
    min_solapado = get_rango_by_max_puntos(puntos_minimos)
    if min_solapado is not None:
        nuevos_puntos_minimos = puntos_minimos + 1
        if get_rango_by_min_puntos(nuevos_puntos_minimos) is not None:
            raise RegistrationError({"detail": "Ya hay un rango con f{puntos_minimos} como máximo y \
									  otro con {nuevos_puntos_minimos} como mínimo"})
    max_solapado = get_rango_by_min_puntos(puntos_maximos)
    if max_solapado is not None:
        nuevos_puntos_maximos = puntos_maximos - 1
        if get_rango_by_min_puntos(nuevos_puntos_maximos) is not None:
            raise RegistrationError({"detail": "Ya hay un rango con f{puntos_maximos} como mínimo y \
									  otro con {nuevos_puntos_maximos} como máximo"})
        
    if nombre == "Sin rango":
        raise RegistrationError({"detail": "No se puede crear un rango con el nombre \"Sin rango\""})
    
    rango = Rango.objects.filter(id=rango_id).first()
    if rango is None:
        raise ValueError("No se encontró el rango a editar")

    rango.nombre = nombre
    rango.color = color
    rango.puntos_minimos = puntos_minimos
    rango.puntos_maximos = puntos_maximos

    rango = Rango(
		nombre=nombre,
		color=color,
		puntos_minimos=puntos_minimos,
		puntos_maximos=puntos_maximos,
	)

    try:
        rango.save()
    except IntegrityError as e:
        msg = str(e)
        if "nombre" in msg:
            raise RegistrationError({"nombre": ["El nombre ya existe"]})
        if "puntos_minimos" in msg:
            raise RegistrationError({"puntos_minimos": ["Los puntos minimos ya existen"]})
        if "puntos_maximos" in msg:
            raise RegistrationError({"puntos_maximos": ["Los puntos maximos ya existen"]})
        raise RegistrationError({"detail": ["No se pudo crear el rango"]})

    return rango


def eliminar_rango_admin(actor, rango_id):
	if not actor.is_staff:
		raise PermissionError("No tienes permiso para eliminar un rango")

	rango = Rango.objects.filter(id=rango_id).first()
	if rango is None:
		raise ValueError("No se encontró el rango a eliminar")

	try:
		rango.delete()
	except Exception:
		raise ValueError("No se pudo eliminar el rango")
