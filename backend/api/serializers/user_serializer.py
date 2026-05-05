from django.contrib.auth import get_user_model
from rest_framework import serializers

from api.selectors import user_selector
from api.services import auth_service

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
        if user_selector.get_users_by_username(value).exists():
            raise serializers.ValidationError("El nombre de usuario ya existe")
        return value

    def validate_email(self, value: str) -> str:
        if user_selector.get_users_by_email(value).exists():
            raise serializers.ValidationError("El correo electrónico ya existe")
        return value

    def create(self, validated_data):
        try:
            return auth_service.registro_usuario(**validated_data)
        except auth_service.RegistrationError as e:
            raise serializers.ValidationError(e.errors)
