from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from tutorials.models import Feedback

User = get_user_model()


class AdminFeedbackViewTest(TestCase):

    def setUp(self):
        # Create an admin user
        self.admin_user = User.objects.create_superuser(
            username="admin", email="admin@example.com", password="adminpassword"
        )

        # Create a regular student user
        self.student_user = User.objects.create_user(
            username="student", email="student@example.com", password="studentpassword"
        )

        # Create sample feedback entries
        self.feedback1 = Feedback.objects.create(
            name="John Doe",
            email="john@example.com",
            message="Great platform!",
        )
        self.feedback2 = Feedback.objects.create(
            name="Jane Doe",
            email="jane@example.com",
            message="Needs more features!",
        )

    def test_feedback_redirects_if_not_logged_in(self):
        """Test that unauthenticated users are redirected to login."""
        response = self.client.get(reverse("admin_feedback"))
        self.assertRedirects(
            response, f"{reverse('log_in')}?next={reverse('admin_feedback')}"
        )

    def test_feedback_renders_correctly_for_admin(self):
        """Test that the feedback page renders correctly for admin users."""
        self.client.login(username="admin", password="adminpassword")
        response = self.client.get(reverse("admin_feedback"))

        # Check correct response and template
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "admin_feedback.html")

        # Check context data
        self.assertIn("feedbacks", response.context)
        feedbacks = response.context["feedbacks"]
        self.assertEqual(feedbacks.count(), 2)

        # Validate ordering (newest first)
        self.assertEqual(feedbacks.first(), self.feedback2)

    def test_feedback_access_denied_for_non_admin_users(self):
        """Test that non-admin users cannot access the feedback page."""
        # Login as a student user
        self.client.login(username="student", password="studentpassword")
        response = self.client.get(reverse("admin_feedback"))
        self.assertEqual(response.status_code, 403)  # Forbidden
