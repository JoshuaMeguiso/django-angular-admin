from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APITestCase

from .serializers import RegistrationSerializer, UserSerializer


class UserModelTests(TestCase):
    def test_user_uses_django_auth_fields_and_hashes_password(self):
        user_model = get_user_model()
        user = user_model.objects.create_user(
            username="jane",
            email="jane@example.com",
            password="correct-horse-battery-staple",
        )

        self.assertEqual(user.username, "jane")
        self.assertEqual(user.email, "jane@example.com")
        self.assertTrue(user.check_password("correct-horse-battery-staple"))
        self.assertNotEqual(user.password, "correct-horse-battery-staple")

    def test_user_is_the_configured_auth_model(self):
        self.assertEqual(get_user_model().__name__, "User")


class UserSerializerTests(TestCase):
    def test_registration_serializer_creates_hashed_password(self):
        serializer = RegistrationSerializer(
            data={
                "username": "jane",
                "email": "jane@example.com",
                "password": "correct-horse-battery-staple",
            }
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)
        user = serializer.save()

        self.assertTrue(user.check_password("correct-horse-battery-staple"))
        self.assertNotIn("password", UserSerializer(user).data)

    def test_registration_serializer_rejects_common_password(self):
        serializer = RegistrationSerializer(
            data={
                "username": "jane",
                "email": "jane@example.com",
                "password": "password",
            }
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("password", serializer.errors)


class RegistrationAPITests(APITestCase):
    def test_register_creates_user_and_returns_public_fields(self):
        response = self.client.post(
            "/api/auth/register/",
            {
                "username": "jane",
                "email": "jane@example.com",
                "password": "correct-horse-battery-staple",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["username"], "jane")
        self.assertNotIn("password", response.data)
        self.assertTrue(get_user_model().objects.filter(username="jane").exists())

    def test_register_rejects_duplicate_username(self):
        get_user_model().objects.create_user(
            username="jane",
            password="correct-horse-battery-staple",
        )

        response = self.client.post(
            "/api/auth/register/",
            {
                "username": "jane",
                "password": "another-valid-password",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class LoginAPITests(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="jane",
            email="jane@example.com",
            password="correct-horse-battery-staple",
        )

    def test_login_returns_token_and_public_user(self):
        response = self.client.post(
            "/api/auth/login/",
            {
                "username": "jane",
                "password": "correct-horse-battery-staple",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["token"])
        self.assertEqual(response.data["user"]["username"], "jane")
        self.assertNotIn("password", response.data["user"])

    def test_login_rejects_invalid_credentials(self):
        response = self.client.post(
            "/api/auth/login/",
            {
                "username": "jane",
                "password": "wrong-password",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ProtectedUserAPITests(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="jane",
            password="correct-horse-battery-staple",
        )

    def test_me_requires_authentication(self):
        response = self.client.get("/api/auth/me/")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_me_returns_authenticated_user(self):
        login_response = self.client.post(
            "/api/auth/login/",
            {
                "username": "jane",
                "password": "correct-horse-battery-staple",
            },
            format="json",
        )
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Token {login_response.data['token']}"
        )

        response = self.client.get("/api/auth/me/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], "jane")
