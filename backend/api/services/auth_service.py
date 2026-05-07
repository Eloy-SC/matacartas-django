from django.db import transaction
from django.db.utils import IntegrityError
from django.contrib.auth import get_user_model
from api.models.perfil import Perfil


class RegistrationError(Exception):
    def __init__(self, errors):
        super().__init__("Registration failed")
        self.errors = errors

@transaction.atomic
def registrar_usuario(username, password, email, nombre, imagen):
    '''
    Registra un nuevo usuario y su perfil asociado. NO es utilizado por administradores para crear usuarios.
    '''
    UserModel = get_user_model()
    try:
        user = UserModel.objects.create_user(username=username, password=password, email=email)
    except IntegrityError as e:
        # No repetimos comprobaciones: el serializer ya valida duplicados.
        # Este bloque cubre la condición de carrera y/o constraints a nivel DB.
        msg = str(e)
        if "username" in msg:
            raise RegistrationError({"username": ["El nombre de usuario ya existe"]})
        if "email" in msg:
            raise RegistrationError({"email": ["El correo electrónico ya existe"]})
        raise RegistrationError({"detail": ["No se pudo crear el usuario"]})

    Perfil.objects.create(user=user, nombre=nombre, imagen=imagen, puntuacion=0)
    return user

