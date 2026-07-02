from rest_framework import serializers

from api.selectors import user_selector


def _username_field(*, required: bool) -> serializers.CharField:
    return serializers.CharField(
        required=required,
        allow_blank=not required,
        max_length=25,
        error_messages={
            "required": "Falta el nombre de usuario",
            "blank": "Falta el nombre de usuario",
            "max_length": "El nombre de usuario es demasiado largo (máx. 25 caracteres)",
        },
    )


def _password_field(*, required: bool) -> serializers.CharField:
    error_messages = {
        "max_length": "La contraseña es demasiado larga (máx. 64 caracteres)",
    }
    if required:
        error_messages = {
            **error_messages,
            "required": "Falta la contraseña",
            "blank": "Falta la contraseña",
        }

    return serializers.CharField(
        required=required,
        allow_blank=not required,
        write_only=True,
        max_length=64,
        error_messages=error_messages,
    )


def _email_field(*, required: bool) -> serializers.EmailField:
    return serializers.EmailField(
        required=required,
        allow_blank=not required,
        max_length=254,
        error_messages={
            "required": "Falta el correo electrónico",
            "blank": "Falta el correo electrónico",
            "invalid": "El correo electrónico no es válido",
            "max_length": "El correo electrónico es demasiado largo (máx. 254 caracteres)",
        },
    )


def _nombre_field(*, required: bool) -> serializers.CharField:
    return serializers.CharField(
        required=required,
        allow_blank=not required,
        max_length=40,
        error_messages={
            "required": "Falta el nombre",
            "blank": "Falta el nombre",
            "max_length": "El nombre es demasiado largo (máx. 40 caracteres)",
        },
    )

def _puntuacion_field(*, required: bool) -> serializers.IntegerField:
    return serializers.IntegerField(
        required=required,
        min_value=0,
        max_value=99999999,
        error_messages={
            "required": "Falta la puntuación",
            "invalid": "La puntuación no es válida",
            "min_value": "La puntuación no puede ser menor que 0",
            "max_value": "La puntuación no puede ser mayor que 99 999 999",
        },
    )


def _imagen_field(*, required: bool) -> serializers.CharField:
    return serializers.CharField(required=required, allow_blank=True, allow_null=True)

def _is_staff_field(*, required: bool) -> serializers.BooleanField:
    return serializers.BooleanField(required=required, default=False)

def _is_staff_optional_field() -> serializers.BooleanField:
    return serializers.BooleanField(required=False)


class _UniqueUsernameEmailMixin:
    def validate_username(self, value: str) -> str:
        qs = user_selector.get_users_by_username(value)
        user = self.context.get("user")
        if user is not None:
            qs = qs.exclude(id=user.id)
        if qs.exists():
            raise serializers.ValidationError("El nombre de usuario ya existe")
        return value

    def validate_email(self, value: str) -> str:
        qs = user_selector.get_users_by_email(value)
        user = self.context.get("user")
        if user is not None:
            qs = qs.exclude(id=user.id)
        if qs.exists():
            raise serializers.ValidationError("El correo electrónico ya existe")
        return value

class RegisterSerializer(_UniqueUsernameEmailMixin, serializers.Serializer):
    username = _username_field(required=True)
    password = _password_field(required=True)
    email = _email_field(required=True)
    nombre = _nombre_field(required=True)
    imagen = _imagen_field(required=False)


class PerfilUpdateSerializer(_UniqueUsernameEmailMixin, serializers.Serializer):
    username = _username_field(required=True)
    password = _password_field(required=False) # Password opcional: si viene vacío o no viene, no se cambia.
    email = _email_field(required=True)
    nombre = _nombre_field(required=True)
    imagen = _imagen_field(required=False)

class UserSerializer(_UniqueUsernameEmailMixin, serializers.Serializer):
    username = _username_field(required=True)
    password = _password_field(required=True)
    email = _email_field(required=True)
    nombre = _nombre_field(required=True)
    imagen = _imagen_field(required=False)
    is_staff = _is_staff_field(required=False)

class AdminUserUpdateSerializer(_UniqueUsernameEmailMixin, serializers.Serializer):
    username = _username_field(required=True)
    password = _password_field(required=False)
    email = _email_field(required=True)
    nombre = _nombre_field(required=True)
    imagen = _imagen_field(required=False)
    is_staff = _is_staff_optional_field()
