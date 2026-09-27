from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class EstadisticasAPITests(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(
            username="estadisticas_api_user",
            password="pass-123",
            email="estadisticas_api@example.com",
            nombre="Usuario Estadisticas API",
        )

    def test_get_estadisticas_globales_requires_authentication(self):
        response = self.client.get(reverse("get-estadisticas-globales"))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_estadisticas_individuales_returns_ok(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.get(reverse("get-estadisticas-individuales"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("partidas_jugadas", response.data)

    def test_get_estadisticas_globales_returns_ok(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.get(reverse("get-estadisticas-globales"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("partidas_totales", response.data)

    def test_get_historial_partidas_returns_empty_list_for_new_user(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.get(reverse("get-historial-partidas"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])
