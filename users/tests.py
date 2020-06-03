from django.test import TestCase, Client
from django.urls import reverse


class TestProfileRegistration(TestCase):
    def setUp(self):
        self.client = Client()
        self.username_for_test = "prikol"
        self.email_for_test = "prikol@yandex.ru"
        self.password_for_test = "Anqewhyq123"

    def test_profile_creation(self):
        response_not_existing_profile = self.client.get(
            reverse("profile", kwargs={"username": self.username_for_test})
        )

        response_registration = self.client.post(
            reverse("signup"),
            {
                "username": self.username_for_test,
                "password1": self.password_for_test,
                "password2": self.password_for_test,
            },
            follow=True,
        )

        response_profile = self.client.get(
            reverse("profile", kwargs={"username": self.username_for_test})
        )
        self.assertEqual(response_not_existing_profile.status_code, 404)
        self.assertEqual(response_registration.status_code, 200)
        self.assertEqual(response_profile.status_code, 200)
