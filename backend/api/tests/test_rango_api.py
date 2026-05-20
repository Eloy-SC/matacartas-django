from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from api.models.rango import Rango


class RangoAPITest(APITestCase):
    def setUp(self):
        UserModel = get_user_model()
        self.admin = UserModel.objects.create_user(
            username="admin",
            password="admin-pass-123",
            email="admin@example.com",
            nombre="Admin",
            is_staff=True,
        )
        self.user = UserModel.objects.create_user(
            username="user",
            password="user-pass-123",
            email="user@example.com",
            nombre="User",
        )
        self.user.puntuacion = 10
        self.user.save()

        self.rango = Rango.objects.create(
            nombre="NovatoTest",
            color=Rango.Color.AZUL_CLARO,
            puntos_minimos=2000,
            puntos_maximos=2099,
        )
        self.rango2 = Rango.objects.create(
            nombre="ExpertoTest",
            color=Rango.Color.AZUL,
            puntos_minimos=2100,
            puntos_maximos=2199,
        )

    def test_listar_rangos_requires_active_user(self):
        url = reverse("listar-rangos")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_listar_rangos_returns_items(self):
        url = reverse("listar-rangos")
        self.client.force_authenticate(user=self.user)

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 2)

    def test_get_rango_returns_404_when_missing(self):
        url = reverse("get-rango", args=[9999])
        self.client.force_authenticate(user=self.user)

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_rango_returns_item(self):
        url = reverse("get-rango", args=[self.rango.id])
        self.client.force_authenticate(user=self.user)

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["nombre"], "NovatoTest")

    def test_get_rango_de_usuario_returns_sin_rango(self):
        url = reverse("get-rango-de-usuario", args=[self.user.id])
        self.client.force_authenticate(user=self.user)

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["nombre"], "Sin rango")

    def test_get_rango_de_usuario_returns_rango(self):
        self.user.puntuacion = 2150
        self.user.save()
        url = reverse("get-rango-de-usuario", args=[self.user.id])
        self.client.force_authenticate(user=self.user)

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["nombre"], "ExpertoTest")

    def test_crear_rango_admin_requires_staff(self):
        url = reverse("crear-rango-admin")
        payload = {
            "nombre": "VeteranoTest",
            "color": Rango.Color.AZUL_CIAN,
            "puntos_minimos": 3000,
            "puntos_maximos": 3099,
        }

        response = self.client.post(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_crear_rango_admin_creates_rango(self):
        url = reverse("crear-rango-admin")
        payload = {
            "nombre": "VeteranoTest",
            "color": Rango.Color.AZUL_CIAN,
            "puntos_minimos": 3000,
            "puntos_maximos": 3099,
        }
        self.client.force_authenticate(user=self.admin)

        response = self.client.post(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Rango.objects.filter(nombre="VeteranoTest").exists())

    def test_crear_rango_admin_rejects_overlap(self):
        url = reverse("crear-rango-admin")
        payload = {
            "nombre": "Solapado",
            "color": Rango.Color.ROJO_CLARO,
            "puntos_minimos": 2050,
            "puntos_maximos": 2150,
        }
        self.client.force_authenticate(user=self.admin)

        response = self.client.post(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_editar_rango_admin_updates_rango(self):
        url = reverse("editar-rango-admin", args=[self.rango.id])
        payload = {
            "nombre": "NovatoTest+",
            "color": Rango.Color.AZUL_CLARO,
            "puntos_minimos": 2000,
            "puntos_maximos": 2089,
        }
        self.client.force_authenticate(user=self.admin)

        response = self.client.put(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.rango.refresh_from_db()
        self.assertEqual(self.rango.nombre, "NovatoTest+")
        self.assertEqual(self.rango.puntos_maximos, 2089)

    def test_editar_rango_admin_returns_404_when_missing(self):
        url = reverse("editar-rango-admin", args=[9999])
        payload = {
            "nombre": "NovatoTest+",
            "color": Rango.Color.AZUL_CLARO,
            "puntos_minimos": 2000,
            "puntos_maximos": 2089,
        }
        self.client.force_authenticate(user=self.admin)

        response = self.client.put(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_eliminar_rango_admin_requires_staff(self):
        url = reverse("eliminar-rango-admin", args=[self.rango.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_eliminar_rango_admin_deletes_rango(self):
        url = reverse("eliminar-rango-admin", args=[self.rango.id])
        self.client.force_authenticate(user=self.admin)

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Rango.objects.filter(id=self.rango.id).exists())

    def test_eliminar_rango_admin_returns_404_when_missing(self):
        url = reverse("eliminar-rango-admin", args=[9999])
        self.client.force_authenticate(user=self.admin)

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
