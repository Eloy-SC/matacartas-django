from django.db import IntegrityError, transaction
from django.contrib.auth import get_user_model
from ..utils.exceptions import ActualizarPerfilError, RegistrationError
from ..selectors.user_selector import (
    get_posicion_top_usuario,
    get_top_users_by_puntos,
    get_users_no_password_count,
    get_users_no_password_paginated,
    get_user_by_id_no_password,
)

@transaction.atomic
def actualizar_perfil(user, *, username, email, nombre, imagen=None, password=None):
    """Actualiza el usuario autenticado y su perfil."""

    UserModel = get_user_model()
    user = UserModel.objects.select_for_update().get(id=user.id)

    user.username = username
    user.email = email
    if password:
        user.set_password(password)
    user.nombre = nombre
    user.imagen = imagen

    try:
        user.save()
    except IntegrityError as e:
        msg = str(e)
        if "username" in msg:
            raise ActualizarPerfilError({"username": ["El nombre de usuario ya existe"]})
        if "email" in msg:
            raise ActualizarPerfilError({"email": ["El correo electrónico ya existe"]})
        raise ActualizarPerfilError({"detail": ["No se pudo actualizar el perfil"]})

    return user

def listar_usuarios_admin(actor, *, page, page_size):
    """
    Devuelve una lista de todos los usuarios y todos sus atributos a excepción de la contraseña. 
    Sólo puede ser utilizado por administradores.
    """

    if not actor.is_staff:
        raise PermissionError("No tienes permiso para listar los usuarios")

    total = get_users_no_password_count()
    offset = (page - 1) * page_size
    items = list(get_users_no_password_paginated(offset, page_size))
    total_pages = max(1, (total + page_size - 1) // page_size)

    return {
        "items": items,
        "page": page,
        "page_size": page_size,
        "total": total,
        "total_pages": total_pages,
    }

def get_usuario_admin(actor, user_id):
    """
    Devuelve un usuario por su ID con todos sus atributos a excepción de la contraseña. 
    Sólo puede ser utilizado por administradores.
    """

    if not actor.is_staff:
        raise PermissionError("No tienes permiso para obtener el usuario")

    return get_user_by_id_no_password(user_id)

def crear_usuario_admin(actor, *, username, password, email, nombre, imagen=None, is_staff=False):
    """
    Crea un nuevo usuario con los datos proporcionados. 
    Sólo puede ser utilizado por administradores.
    """

    if not actor.is_staff:
        raise PermissionError("No tienes permiso para crear un usuario")

    UserModel = get_user_model()
    user = UserModel(username=username, password=password, email=email, nombre=nombre, imagen=imagen, is_staff=is_staff)

    try:
        user.save()
    except IntegrityError as e:
        msg = str(e)
        if "username" in msg:
            raise RegistrationError({"username": ["El nombre de usuario ya existe"]})
        if "email" in msg:
            raise RegistrationError({"email": ["El correo electrónico ya existe"]})
        raise RegistrationError({"detail": ["No se pudo crear el usuario"]})

    return user

def editar_usuario_admin(actor, user_id, *, username, password=None, email, nombre, imagen=None, is_staff=None):
    """
    Edita un usuario por su ID. 
    Sólo puede ser utilizado por administradores.
    """
    if not actor.is_staff:
        raise PermissionError("No tienes permiso para editar un usuario")

    UserModel = get_user_model()
    user = UserModel.objects.filter(id=user_id).first()
    if user is None:
        raise ValueError("No se encontró el usuario")

    user.username = username
    user.email = email
    if password:
        user.set_password(password)
    user.nombre = nombre
    user.imagen = imagen
    if is_staff is False and user.is_staff:
        remaining_admins = UserModel.objects.filter(is_staff=True).exclude(id=user_id)
        if not remaining_admins.exists():
            raise RegistrationError({
                "detail": [
                    "No se puede retirar permisos de administracion a este usuario porque es el unico administrador"
                ]
            })
    if is_staff is False and actor.id == user_id:
        raise RegistrationError({
            "detail": [
                "No se puedes retirarte permisos de administracion a ti mismo"
            ]
        })

    if is_staff is not None:
        user.is_staff = is_staff

    try:
        user.save()
    except IntegrityError as e:
        msg = str(e)
        if "username" in msg:
            raise RegistrationError({"username": ["El nombre de usuario ya existe"]})
        if "email" in msg:
            raise RegistrationError({"email": ["El correo electrónico ya existe"]})
        raise RegistrationError({"detail": ["No se pudo editar el usuario"]})

    return user

def eliminar_usuario_admin(actor, user_id):
    """
    Elimina un usuario por su ID. 
    Sólo puede ser utilizado por administradores.
    """

    if not actor.is_staff:
        raise PermissionError("No tienes permiso para eliminar un usuario")

    UserModel = get_user_model()
    user = UserModel.objects.filter(id=user_id).first()
    if user is None:
        raise ValueError("No se encontró el usuario")

    try: 
        user.delete()
    except Exception as e:
        raise ValueError("No se pudo eliminar el usuario")
    
def listar_top_usuarios(actor):
    """
    Devuelve una lista de los 10 usuarios con mayor puntuación. 
    Puede ser utilizado por cualquier usuario autenticado.
    Si el actor no está entre esos 10 usuarios, también se incluye su usuario al final de la lista.
    """

    if not actor.is_authenticated:
        raise PermissionError("No tienes permiso para listar los usuarios")

    usuarios = list(get_top_users_by_puntos(10))
    for u in usuarios:
        u["posicion"] = usuarios.index(u) + 1
    if not any(u["id"] == actor.id for u in usuarios):
        actor_data = get_user_by_id_no_password(actor.id)
        if actor_data:
            actor_data["posicion"] = get_posicion_top_usuario(actor.id)
            usuarios.append(actor_data)
        else:
            raise ValueError("No se encontró el usuario autenticado")
    
    return usuarios