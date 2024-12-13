from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from tutorials.models import Tutor

User = get_user_model()


class TutorSignUpViewTest(TestCase):
    
    def setUp(self):
        self.url = reverse("tutor_sign_up")

    def test_tutor_sign_up_page_renders_correct_template(self):
        """Test that the correct template is rendered for tutor signup."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "tutor_sign_up.html")

    def test_tutor_sign_up_successful(self):
        """Test successful tutor signup."""
        response = self.client.post(self.url, {
            "username": "newtutor",
            "email": "newtutor@example.com",
            "password1": "securepassword123",
            "password2": "securepassword123",
        })
        
        self.assertRedirects(response, reverse("dashboard"))
        self.assertTrue(User.objects.filter(username="newtutor").exists())
        self.assertTrue(Tutor.objects.filter(user__username="newtutor").exists())

    def test_tutor_sign_up_password_mismatch(self):
        """Test tutor signup fails due to mismatched passwords."""
        response = self.client.post(self.url, {
            "username": "newtutor",
            "email": "newtutor@example.com",
            "password1": "securepassword123",
            "password2": "wrongpassword123",
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "The two password fields didn’t match.")
        self.assertFalse(User.objects.filter(username="newtutor").exists())

    def test_tutor_sign_up_existing_email(self):
        """Test signup fails if email is already registered."""
        User.objects.create_user(
            username="existingtutor",
            email="existingtutor@example.com",
            password="securepassword123"
        )
        
        response = self.client.post(self.url, {
            "username": "newtutor",
            "email": "existingtutor@example.com",
            "password1": "securepassword123",
            "password2": "securepassword123",
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "A user with that email already exists.")
        self.assertFalse(User.objects.filter(username="newtutor").exists())

    def test_redirect_if_logged_in(self):
        """Test that logged-in users are redirected."""
        user = User.objects.create_user(
            username="loggedintutor", email="loggedin@example.com", password="securepassword123"
        )
        self.client.login(username="loggedintutor", password="securepassword123")

        response = self.client.get(self.url)
        self.assertRedirects(response, reverse("dashboard"))
