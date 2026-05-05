from django.db import transaction
from django.db.utils import IntegrityError
from django.contrib.auth import get_user_model
from api.models.perfil import Perfil
from api.selectors import user_selector


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
    except IntegrityError:
        errors = {}
        if user_selector.get_users_by_username(username).exists():
            errors["username"] = ["El nombre de usuario ya existe"]
        if user_selector.get_users_by_email(email).exists():
            errors["email"] = ["El correo electrónico ya existe"]
        if not errors:
            errors["detail"] = ["No se pudo crear el usuario"]
        raise RegistrationError(errors)

    Perfil.objects.create(user=user, nombre=nombre, imagen=imagen, puntuacion=0)
    return user

