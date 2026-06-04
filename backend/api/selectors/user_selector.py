from django.contrib.auth import get_user_model
from django.db.models import Q

def get_users_by_username(username):
    UserModel = get_user_model()
    return UserModel.objects.filter(username=username)

def get_users_by_email(email):
    UserModel = get_user_model()
    return UserModel.objects.filter(email=email)

def get_users_no_password():
    UserModel = get_user_model()
    return UserModel.objects.all().values("id", "username", "email", "nombre", "puntuacion", "imagen", "is_staff", "is_active")

def _build_users_queryset(search=None, is_active=None, is_staff=None, rango_interval=None):
    UserModel = get_user_model()
    queryset = UserModel.objects.all()

    if search:
        search = search.strip()
        if search:
            queryset = queryset.filter(
                Q(username__icontains=search)
                | Q(email__icontains=search)
                | Q(nombre__icontains=search)
            )

    if is_active is not None:
        queryset = queryset.filter(is_active=is_active)

    if is_staff is not None:
        queryset = queryset.filter(is_staff=is_staff)

    if rango_interval:
        puntos_minimos, puntos_maximos = rango_interval
        queryset = queryset.filter(
            puntuacion__gte=puntos_minimos,
            puntuacion__lte=puntos_maximos,
        )

    return queryset

def get_users_no_password_paginated(
    offset,
    limit,
    *,
    search=None,
    is_active=None,
    is_staff=None,
    rango_interval=None,
    ordering=None,
):
    queryset = _build_users_queryset(
        search=search,
        is_active=is_active,
        is_staff=is_staff,
        rango_interval=rango_interval,
    )

    order_fields = []
    if ordering:
        order_fields.append(ordering)
        if ordering.lstrip("-") != "id":
            order_fields.append("id")
    else:
        order_fields.append("id")

    return (
        queryset.values("id", "username", "email", "nombre", "puntuacion", "imagen", "is_staff", "is_active")
        .order_by(*order_fields)[offset:offset + limit]
    )

def get_users_no_password_count(*, search=None, is_active=None, is_staff=None, rango_interval=None):
    queryset = _build_users_queryset(
        search=search,
        is_active=is_active,
        is_staff=is_staff,
        rango_interval=rango_interval,
    )
    return queryset.count()

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