from django.contrib.auth import get_user_model
from django.test import TestCase

from api.models.recompensa import Logro, RequisitoLogro
from api.services import logro_service
from api.utils.exceptions import RegistrationError


class LogroServiceTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.admin = User.objects.create_user(
            username="logro_admin",
            password="pass-123",
            email="logro_admin@example.com",
            nombre="Admin Logros",
            is_staff=True,
        )
        self.user = User.objects.create_user(
            username="logro_user",
            password="pass-123",
            email="logro_user@example.com",
            nombre="Usuario Logros",
        )

    def test_crear_logro_creates_requirement(self):
        logro = logro_service.crear_logro(
            self.admin,
            nombre="Primer logro",
            descripcion="Descripcion",
            requisitos=[{"requisito": RequisitoLogro.Requisito.PARTIDAS_GANADAS}],
        )

        self.assertEqual(logro.nombre, "Primer logro")
        self.assertEqual(logro.requisitologro_set.count(), 1)

    def test_listar_logros_usuario_paginated_requires_active_user(self):
        self.user.is_active = False
        self.user.save(update_fields=["is_active"])

        with self.assertRaises(PermissionError):
            logro_service.listar_logros_usuario_paginated(self.user, page=1, page_size=10)

    def test_crear_logro_requires_at_least_one_requirement(self):
        with self.assertRaises(ValueError):
            logro_service.crear_logro(
                self.admin,
                nombre="Logro sin requisitos",
                descripcion="Descripcion",
                requisitos=[],
            )

    def test_crear_logro_rejects_duplicate_name(self):
        logro_service.crear_logro(
            self.admin,
            nombre="Logro duplicado",
            descripcion="Descripcion",
            requisitos=[{"requisito": RequisitoLogro.Requisito.PARTIDAS_GANADAS}],
        )

        with self.assertRaises(RegistrationError):
            logro_service.crear_logro(
                self.admin,
                nombre="Logro duplicado",
                descripcion="Otra descripcion",
                requisitos=[{"requisito": RequisitoLogro.Requisito.PARTIDAS_GANADAS}],
            )

    def test_eliminar_logro_admin_removes_item(self):
        logro = Logro.objects.create(nombre="Logro eliminable", descripcion="Descripcion")

        logro_service.eliminar_logro_admin(self.admin, logro.id)

        self.assertFalse(Logro.objects.filter(id=logro.id).exists())

    def test_obtener_requisitos_logro_returns_values_for_staff(self):
        logro = logro_service.crear_logro(
            self.admin,
            nombre="Logro requisitos",
            descripcion="Descripcion",
            requisitos=[{"requisito": RequisitoLogro.Requisito.PARTIDAS_GANADAS, "valor_necesario": 2}],
        )

        requisitos = logro_service.obtener_requisitos_logro(self.admin, logro.id)

        self.assertEqual(requisitos[0]["valor_necesario"], 2)
