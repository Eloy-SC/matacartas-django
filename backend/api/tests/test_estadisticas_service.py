from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.test import TestCase

from api.services import estadisticas_service


class EstadisticasServiceTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(
            username="estadisticas_user",
            password="pass-123",
            email="estadisticas@example.com",
            nombre="Usuario Estadisticas",
        )

    def test_get_estadisticas_globales_requires_authentication(self):
        with self.assertRaises(PermissionError):
            estadisticas_service.get_estadisticas_globales(AnonymousUser())

    def test_get_estadisticas_individuales_returns_keys(self):
        result = estadisticas_service.get_estadisticas_individuales(self.user)

        self.assertIn("partidas_jugadas", result)
        self.assertIn("puntos_ganados", result)

    def test_get_estadisticas_globales_returns_expected_sections(self):
        result = estadisticas_service.get_estadisticas_globales(self.user)

        self.assertIn("partidas_totales", result)
        self.assertIn("partidas_finalizadas", result)

    def test_get_estadisticas_individuales_returns_zero_for_new_user(self):
        result = estadisticas_service.get_estadisticas_individuales(self.user)

        self.assertEqual(result["partidas_jugadas"], 0)

    def test_get_historial_partidas_returns_empty_for_new_user(self):
        result = estadisticas_service.get_historial_partidas(self.user)

        self.assertEqual(result, [])
