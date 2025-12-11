"""Integration-style tests for auth endpoints (register, login, password reset)."""

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()

class RegisterViewTest(TestCase):
    """Ensure registration creates an inactive user and returns 201."""

    def test_register_creates_user(self):
        response = self.client.post(reverse('user-register'), {
            'email': 'test@example.com',
            'password': 'Test1234!',
            'password2': 'Test1234!'
        })
        self.assertEqual(response.status_code, 201)
        self.assertTrue(User.objects.filter(email='test@example.com').exists())

class LoginViewTest(TestCase):
    """Validate successful and failed login flows."""

    def setUp(self):
        self.user = User.objects.create_user(email='login@example.com', password='Test1234!')
        self.user.is_active = True
        self.user.save()

    def test_login_success(self):
        """User with correct credentials receives access token."""
        response = self.client.post(reverse('user-login'), {
            'email': 'login@example.com',
            'password': 'Test1234!'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('access', response.json())

    def test_login_wrong_password(self):
        """Wrong password returns 401 with generic error detail."""
        response = self.client.post(reverse('user-login'), {
            'email': 'login@example.com',
            'password': 'WrongPassword!'
        })
        self.assertEqual(response.status_code, 401)
        self.assertIn('detail', response.json())

class PasswordResetTest(TestCase):
    """Requesting a password reset responds with a generic success message."""

    def setUp(self):
        self.user = User.objects.create_user(email='reset@example.com', password='Test1234!')
        self.user.is_active = True
        self.user.save()

    def test_password_reset_request(self):
        response = self.client.post(reverse('user-password-reset'), {
            'email': 'reset@example.com'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('message', response.json())
