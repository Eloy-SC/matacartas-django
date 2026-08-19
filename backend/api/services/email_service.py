from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode


User = get_user_model()


def enviar_email_recuperacion_password(usuario):
    uid = urlsafe_base64_encode(force_bytes(usuario.pk))
    token = default_token_generator.make_token(usuario)

    reset_url = (
        f"{settings.FRONTEND_URL}"
        f"/restablecer-password/{uid}/{token}"
    )

    contexto = {
        "usuario": usuario,
        "reset_url": reset_url,
    }

    html_content = render_to_string(
        "emails/password_reset.html",
        contexto,
    )

    email = EmailMultiAlternatives(
        subject="Recuperación de contraseña - Matacartas",
        body=(
            "Has solicitado recuperar tu contraseña de Matacartas.\n\n"
            f"Accede al siguiente enlace:\n{reset_url}\n\n"
            "Si no has solicitado este cambio, puedes ignorar este correo."
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[usuario.email],
    )

    email.attach_alternative(
        html_content,
        "text/html",
    )

    email.send()

def enviar_email_verificacion(usuario):
    uid = urlsafe_base64_encode(
        force_bytes(usuario.pk)
    )

    token = default_token_generator.make_token(
        usuario
    )

    verification_url = (
        f"{settings.FRONTEND_URL}"
        f"/verificar-email/{uid}/{token}"
    )

    contexto = {
        "usuario": usuario,
        "verification_url": verification_url,
    }

    html_content = render_to_string(
        "emails/verification_email.html",
        contexto,
    )

    email = EmailMultiAlternatives(
        subject="Verifica tu cuenta - Matacartas",
        body=(
            "Verifica tu cuenta de Matacartas "
            f"accediendo al siguiente enlace:\n\n"
            f"{verification_url}"
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[usuario.email],
    )

    email.attach_alternative(
        html_content,
        "text/html",
    )

    email.send()