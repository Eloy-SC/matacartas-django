from django.contrib.auth import get_user_model
from django.test import TestCase

from api.models.notificacion import SolicitudAmistad
from api.models.amistad import Amistad
from api.services import notificacion_service


class NotificacionServiceTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.sender = User.objects.create_user(
            username="notificacion_sender",
            password="pass-123",
            email="sender@example.com",
            nombre="Emisor",
        )
        self.receiver = User.objects.create_user(
            username="notificacion_receiver",
            password="pass-123",
            email="receiver@example.com",
            nombre="Receptor",
        )

    def test_enviar_solicitud_amistad_creates_notification(self):
        solicitud = notificacion_service.enviar_solicitud_amistad(
            self.sender,
            self.receiver.id,
        )

        self.assertEqual(solicitud.receptor_id, self.receiver.id)
        self.assertTrue(SolicitudAmistad.objects.filter(id=solicitud.id).exists())

    def test_contestar_solicitud_amistad_accepts_and_creates_friendship(self):
        solicitud = SolicitudAmistad.objects.create(
            emisor=self.sender,
            receptor=self.receiver,
        )

        notificacion_service.contestar_solicitud_amistad(
            self.receiver,
            solicitud.id,
            aceptar=True,
        )

        self.assertFalse(SolicitudAmistad.objects.filter(id=solicitud.id).exists())

    def test_enviar_solicitud_amistad_rejects_self(self):
        with self.assertRaises(ValueError):
            notificacion_service.enviar_solicitud_amistad(self.sender, self.sender.id)

    def test_enviar_solicitud_amistad_rejects_duplicate(self):
        notificacion_service.enviar_solicitud_amistad(self.sender, self.receiver.id)

        with self.assertRaises(ValueError):
            notificacion_service.enviar_solicitud_amistad(self.sender, self.receiver.id)

    def test_contestar_solicitud_amistad_reject_removes_request(self):
        solicitud = SolicitudAmistad.objects.create(emisor=self.sender, receptor=self.receiver)

        notificacion_service.contestar_solicitud_amistad(self.receiver, solicitud.id, aceptar=False)

        self.assertFalse(SolicitudAmistad.objects.filter(id=solicitud.id).exists())

    def test_contestar_solicitud_amistad_accept_creates_friendship(self):
        solicitud = SolicitudAmistad.objects.create(emisor=self.sender, receptor=self.receiver)

        notificacion_service.contestar_solicitud_amistad(self.receiver, solicitud.id, aceptar=True)

        self.assertTrue(Amistad.objects.filter(usuario1=self.sender, usuario2=self.receiver).exists())

    def test_listar_notificaciones_returns_pagination_metadata(self):
        SolicitudAmistad.objects.create(emisor=self.sender, receptor=self.receiver)

        result = notificacion_service.listar_notificaciones(self.receiver)

        self.assertEqual(result["total"], 1)
        self.assertEqual(result["page"], 1)
