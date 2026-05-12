from django.db import transaction
from django.db.utils import IntegrityError
from django.contrib.auth import get_user_model
from ..utils.exceptions import RegistrationError
from ..selectors import user_selector

@transaction.atomic
def registrar_usuario(username, password, email, nombre, imagen):
    '''
    Registra un nuevo usuario y su perfil asociado. NO es utilizado por administradores para crear usuarios.
    '''
    Usuario = get_user_model()
    try:
        user = Usuario.objects.create_user(username=username, password=password, 
                                           email=email, nombre=nombre, 
                                           imagen=imagen, puntuacion=0)
    except IntegrityError as e:
        msg = str(e)
        if "username" in msg:
            raise RegistrationError({"username": ["El nombre de usuario ya existe"]})
        if "email" in msg:
            raise RegistrationError({"email": ["El correo electrónico ya existe"]})
        raise RegistrationError({"detail": ["No se pudo crear el usuario"]})

    return user

@transaction.atomic
def me(user):
    '''
    Devuelve el usuario autenticado. No es utilizado por administradores.
    '''
    Usuario = get_user_model()
    user = Usuario.objects.get(id=user.id)
    return user