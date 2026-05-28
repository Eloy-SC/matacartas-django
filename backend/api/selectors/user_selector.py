from django.contrib.auth import get_user_model

def get_users_by_username(username):
    UserModel = get_user_model()
    return UserModel.objects.filter(username=username)

def get_users_by_email(email):
    UserModel = get_user_model()
    return UserModel.objects.filter(email=email)

def get_users_no_password():
    UserModel = get_user_model()
    return UserModel.objects.all().values("id", "username", "email", "nombre", "puntuacion", "imagen", "is_staff", "is_active")

def get_users_no_password_paginated(offset, limit):
    UserModel = get_user_model()
    return (
        UserModel.objects.all()
        .values("id", "username", "email", "nombre", "puntuacion", "imagen", "is_staff", "is_active")
        .order_by("id")[offset:offset + limit]
    )

def get_users_no_password_count():
    UserModel = get_user_model()
    return UserModel.objects.count()

def get_user_by_id_no_password(user_id):
    UserModel = get_user_model()
    return UserModel.objects.filter(id=user_id).values("id", "username", "email", "nombre", "puntuacion", "imagen", "is_staff", "is_active").first()

def get_puntos_by_user_id(user_id):
    UserModel = get_user_model()
    return UserModel.objects.filter(id=user_id).values("puntuacion").first().get("puntuacion", 0)

def get_top_users_by_puntos(limit):
    UserModel = get_user_model()
    return UserModel.objects.all().values("id", "username", "email", "nombre", "puntuacion", "imagen").order_by("-puntuacion")[:limit]

def get_posicion_top_usuario(user_id):
    UserModel = get_user_model()
    users = UserModel.objects.all().values("id", "puntuacion").order_by("-puntuacion")
    for index, user in enumerate(users, start=1):
        if user["id"] == user_id:
            return index
    return None