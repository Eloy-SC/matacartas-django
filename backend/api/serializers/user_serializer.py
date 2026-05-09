from rest_framework import serializers

from api.selectors import user_selector

class UserSerializer(serializers.Serializer):
    username = serializers.CharField(
        required=True,
        allow_blank=False,
        max_length=25,
        error_messages={
            "required": "Falta el nombre de usuario",
            "blank": "Falta el nombre de usuario",
            "max_length": "El nombre de usuario es demasiado largo (máx. 25 caracteres)",
        },
    )

    password = serializers.CharField(
        required=True,
        allow_blank=False,
        write_only=True,
        max_length=64,
        error_messages={
            "required": "Falta la contraseña",
            "blank": "Falta la contraseña",
            "max_length": "La contraseña es demasiado larga (máx. 64 caracteres)",
        },
    )

    email = serializers.EmailField(
        required=True,
        allow_blank=False,
        max_length=254,
        error_messages={
            "required": "Falta el correo electrónico",
            "blank": "Falta el correo electrónico",
            "invalid": "El correo electrónico no es válido",
            "max_length": "El correo electrónico es demasiado largo (máx. 254 caracteres)",
        },
    )

    # Campos del perfil
    nombre = serializers.CharField(
        required=True,
        allow_blank=False,
        max_length=25,
        error_messages={
            "required": "Falta el nombre",
            "blank": "Falta el nombre",
            "max_length": "El nombre es demasiado largo (máx. 25 caracteres)",
        },
    )
    imagen = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    def validate_username(self, value: str) -> str:
        if (
            not value.isascii()
            or not value.islower()
            or not all(ch.isalnum() or ch == "_" for ch in value)
        ):
            raise serializers.ValidationError(
                "El nombre de usuario solo puede contener letras minúsculas, números y guiones bajos."
            )

        if user_selector.get_users_by_username(value).exists():
            raise serializers.ValidationError("El nombre de usuario ya existe")
        return value

    def validate_email(self, value: str) -> str:
        if user_selector.get_users_by_email(value).exists():
            raise serializers.ValidationError("El correo electrónico ya existe")
        return value


class PerfilUpdateSerializer(serializers.Serializer):
    username = serializers.CharField(
        required=True,
        allow_blank=False,
        max_length=25,
        error_messages={
            "required": "Falta el nombre de usuario",
            "blank": "Falta el nombre de usuario",
            "max_length": "El nombre de usuario es demasiado largo (máx. 25 caracteres)",
        },
    )

    # Password opcional: si viene vacío o no viene, no se cambia.
    password = serializers.CharField(
        required=False,
        allow_blank=True,
        write_only=True,
        max_length=64,
        error_messages={
            "max_length": "La contraseña es demasiado larga (máx. 64 caracteres)",
        },
    )

    email = serializers.EmailField(
        required=True,
        allow_blank=False,
        max_length=254,
        error_messages={
            "required": "Falta el correo electrónico",
            "blank": "Falta el correo electrónico",
            "invalid": "El correo electrónico no es válido",
            "max_length": "El correo electrónico es demasiado largo (máx. 254 caracteres)",
        },
    )

    nombre = serializers.CharField(
        required=True,
        allow_blank=False,
        max_length=25,
        error_messages={
            "required": "Falta el nombre",
            "blank": "Falta el nombre",
            "max_length": "El nombre es demasiado largo (máx. 25 caracteres)",
        },
    )

    imagen = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    def validate_username(self, value: str) -> str:
        if (
            not value.isascii()
            or not value.islower()
            or not all(ch.isalnum() or ch == "_" for ch in value)
        ):
            raise serializers.ValidationError(
                "El nombre de usuario solo puede contener letras minúsculas, números y guiones bajos."
            )

        user = self.context.get("user")
        qs = user_selector.get_users_by_username(value)
        if user is not None:
            qs = qs.exclude(id=user.id)
        if qs.exists():
            raise serializers.ValidationError("El nombre de usuario ya existe")

        return value

    def validate_email(self, value: str) -> str:
        user = self.context.get("user")
        qs = user_selector.get_users_by_email(value)
        if user is not None:
            qs = qs.exclude(id=user.id)
        if qs.exists():
            raise serializers.ValidationError("El correo electrónico ya existe")
        return value
