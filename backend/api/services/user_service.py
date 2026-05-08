from django.db import IntegrityError, transaction
from django.contrib.auth import get_user_model

from ..models.perfil import Perfil
from ..utils.exceptions import ActualizarPerfilError


@transaction.atomic
def actualizar_perfil(user, *, username, email, nombre, imagen=None, password=None):
    """Actualiza el usuario autenticado y su perfil."""

    UserModel = get_user_model()
    user = UserModel.objects.select_for_update().get(id=user.id)
    perfil = Perfil.objects.select_for_update().get(user=user)

    user.username = username
    user.email = email
    if password:
        user.set_password(password)

    perfil.nombre = nombre
    perfil.imagen = imagen

    try:
        user.save()
        perfil.save()
    except IntegrityError as e:
        msg = str(e)
        if "username" in msg:
            raise ActualizarPerfilError({"username": ["El nombre de usuario ya existe"]})
        if "email" in msg:
            raise ActualizarPerfilError({"email": ["El correo electrónico ya existe"]})
        raise ActualizarPerfilError({"detail": ["No se pudo actualizar el perfil"]})

    return user
