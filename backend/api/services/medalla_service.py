from django.db import IntegrityError

from ..models.recompensa import Medalla
from ..selectors.medalla_selector import get_medalla_by_id, get_medalla_by_nombre, list_medallas
from ..utils.exceptions import RegistrationError


def listar_medallas(actor):
    if not actor.is_active:
        raise PermissionError("No tienes permiso para listar medallas")

    return list_medallas()


def get_medalla(actor, medalla_id):
    if not actor.is_active:
        raise PermissionError("No tienes permiso para obtener la medalla")

    return get_medalla_by_id(medalla_id)


def crear_medalla_admin(actor, *, nombre, categoria, imagen=None):
    if not actor.is_staff:
        raise PermissionError("No tienes permiso para crear una medalla")

    if get_medalla_by_nombre(nombre) is not None:
        raise RegistrationError({"nombre": ["El nombre ya existe"]})

    medalla = Medalla(nombre=nombre, categoria=categoria, imagen=imagen)

    try:
        medalla.save()
    except IntegrityError as e:
        msg = str(e)
        if "nombre" in msg:
            raise RegistrationError({"nombre": ["El nombre ya existe"]})
        raise RegistrationError({"detail": ["No se pudo crear la medalla"]})

    return medalla


def editar_medalla_admin(actor, medalla_id, *, nombre, categoria, imagen=None):
    if not actor.is_staff:
        raise PermissionError("No tienes permiso para editar una medalla")

    medalla = get_medalla_by_id(medalla_id)
    if medalla is None:
        raise ValueError("No se encontró la medalla a editar")

    medalla_nombre_repetido = get_medalla_by_nombre(nombre)
    if medalla_nombre_repetido is not None and medalla_nombre_repetido.id != medalla_id:
        raise RegistrationError({"nombre": ["El nombre ya existe"]})

    medalla.nombre = nombre
    medalla.categoria = categoria
    medalla.imagen = imagen

    try:
        medalla.save()
    except IntegrityError as e:
        msg = str(e)
        if "nombre" in msg:
            raise RegistrationError({"nombre": ["El nombre ya existe"]})
        raise RegistrationError({"detail": ["No se pudo editar la medalla"]})

    return medalla


def eliminar_medalla_admin(actor, medalla_id):
    if not actor.is_staff:
        raise PermissionError("No tienes permiso para eliminar una medalla")

    medalla = get_medalla_by_id(medalla_id)
    if medalla is None:
        raise ValueError("No se encontró la medalla a eliminar")

    try:
        medalla.delete()
    except Exception:
        raise ValueError("No se pudo eliminar la medalla")
