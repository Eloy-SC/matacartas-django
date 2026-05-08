from django.contrib.auth import get_user_model

from ..models.perfil import Perfil

def get_users_by_username(username):
    UserModel = get_user_model()
    return UserModel.objects.filter(username=username)

def get_users_by_email(email):
    UserModel = get_user_model()
    return UserModel.objects.filter(email=email)

def get_perfil_by_user_id(user_id):
    try:
        perfil = Perfil.objects.get(user_id=user_id)
        return perfil
    except Perfil.DoesNotExist:
        return None