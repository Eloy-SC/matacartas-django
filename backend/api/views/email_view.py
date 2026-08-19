from django.contrib.auth import get_user_model
from django.utils.encoding import force_str
from django.contrib.auth.forms import SetPasswordForm
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status

from api.serializers.password_reset_serializer import (
    PasswordResetRequestSerializer, PasswordResetConfirmSerializer
)
from api.services.email_service import (
    enviar_email_recuperacion_password,
)


User = get_user_model()


@api_view(["POST"])
@permission_classes([AllowAny])
def solicitar_recuperacion_password(request):
    serializer = PasswordResetRequestSerializer(
        data=request.data
    )

    serializer.is_valid(raise_exception=True)

    email = serializer.validated_data["email"]

    usuario = User.objects.filter(
        email__iexact=email,
        is_active=True,
    ).first()

    if usuario is not None:
        enviar_email_recuperacion_password(usuario)

    return Response(
        {
            "detail": (
                "Si existe una cuenta asociada a ese correo, "
                "recibirás un email con las instrucciones."
            )
        },
        status=status.HTTP_200_OK,
    )

@api_view(["POST"])
@permission_classes([AllowAny])
def confirmar_recuperacion_password(request):
    serializer = PasswordResetConfirmSerializer(
        data=request.data
    )

    serializer.is_valid(raise_exception=True)

    uid = serializer.validated_data["uid"]
    token = serializer.validated_data["token"]
    nueva_password = serializer.validated_data["new_password"]

    try:
        uid_decoded = force_str(
            urlsafe_base64_decode(uid)
        )

        usuario = User.objects.get(
            pk=uid_decoded
        )

    except (
        TypeError,
        ValueError,
        OverflowError,
        User.DoesNotExist,
    ):
        return Response(
            {
                "detail": (
                    "El enlace de recuperación "
                    "no es válido."
                )
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    if not default_token_generator.check_token(
        usuario,
        token,
    ):
        return Response(
            {
                "detail": (
                    "El enlace de recuperación "
                    "no es válido o ha caducado."
                )
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    form = SetPasswordForm(
        user=usuario,
        data={
            "new_password1": nueva_password,
            "new_password2": nueva_password,
        },
    )

    if not form.is_valid():
        return Response(
            {
                "detail": (
                    "La contraseña no cumple "
                    "los requisitos."
                    "No debe ser común."
                    "Debe tener al menos 10 "
                    "caracteres."
                    "No debe tener sólo digitos"
                    "No debe ser similar a la"
                    "información personal."
                ),
                "errors": form.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    form.save()

    return Response(
        {
            "detail": (
                "La contraseña se ha cambiado "
                "correctamente."
            )
        },
        status=status.HTTP_200_OK,
    )