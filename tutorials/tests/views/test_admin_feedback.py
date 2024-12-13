from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from tutorials.models import Feedback

User = get_user_model()

class AdminFeedbackViewTest(TestCase):

    def setUp(self):
        # Create an admin user
        self.admin_user = User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="adminpassword"
        )

        # Create a regular user
        self.regular_user = User.objects.create_user(
            username="user",
            email="user@example.com",
            password="userpassword"
        )

        # Create feedback objects
        self.feedback1 = Feedback.objects.create(
            name="John Doe",
            email="john@example.com",
            message="This is the first feedback."
        )
        self.feedback2 = Feedback.objects.create(
            name="Jane Smith",
            email="jane@example.com",
            message="This is the second feedback."
        )

    def test_feedback_access_denied_for_non_admin_users(self):
        self.client.login(username="user", password="userpassword")
        response = self.client.get(reverse("admin_feedback"))
        self.assertEqual(response.status_code, 302)  # Forbidden

    def test_feedback_access_for_admin_users(self):
        self.client.login(username="admin", password="adminpassword")
        response = self.client.get(reverse("admin_feedback"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "admin_feedback.html")

    def test_feedback_displayed(self):
        self.client.login(username="admin", password="adminpassword")
        response = self.client.get(reverse("admin_feedback"))
        self.assertContains(response, "This is the first feedback.")
        self.assertContains(response, "This is the second feedback.")
        self.assertEqual(len(response.context["feedbacks"]), 2)
