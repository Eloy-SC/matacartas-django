from django.db import IntegrityError, transaction
from django.contrib.auth import get_user_model
from ..utils.exceptions import ActualizarPerfilError


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

def listar_usuarios_admin(user):
    """
    Devuelve una lista de todos los usuarios y todos sus atributos a excepción de la contraseña. 
    Sólo puede ser utilizado por usuarios staff.
    """

    if not user.is_staff:
        raise PermissionError("No tienes permiso para listar los usuarios")

    UserModel = get_user_model()
    return UserModel.objects.all()