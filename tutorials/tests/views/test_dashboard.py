from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


class DashboardViewTest(TestCase):

    def setUp(self):
        # Create users with different roles
        self.student_user = User.objects.create_user(
            username="student", email="student@example.com", password="studentpassword", role="student"
        )
        self.tutor_user = User.objects.create_user(
            username="tutor", email="tutor@example.com", password="tutorpassword", role="tutor"
        )
        self.admin_user = User.objects.create_superuser(
            username="admin", email="admin@example.com", password="adminpassword", role="admin"
        )
        self.invalid_user = User.objects.create_user(
            username="unknown", email="unknown@example.com", password="unknownpassword", role="unknown"
        )

    def test_dashboard_redirects_if_not_logged_in(self):
        """Test that the dashboard view redirects if the user is not logged in."""
        response = self.client.get(reverse("dashboard"))
        self.assertRedirects(
            response, f"{reverse('log_in')}?next={reverse('dashboard')}"
        )

    def test_dashboard_redirects_to_student_dashboard(self):
        """Test that a student user is redirected to the student dashboard."""
        self.client.login(username="student", password="studentpassword")
        response = self.client.get(reverse("dashboard"))
        self.assertRedirects(response, reverse("student_dashboard"))

    def test_dashboard_redirects_to_tutor_dashboard(self):
        """Test that a tutor user is redirected to the tutor dashboard."""
        self.client.login(username="tutor", password="tutorpassword")
        response = self.client.get(reverse("dashboard"))
        self.assertRedirects(response, reverse("tutor_dashboard"))

    def test_dashboard_redirects_to_admin_dashboard(self):
        """Test that an admin user is redirected to the admin dashboard."""
        self.client.login(username="admin", password="adminpassword")
        response = self.client.get(reverse("dashboard"))
        self.assertRedirects(response, reverse("admin_dashboard"))

    def test_dashboard_redirects_invalid_user_role(self):
        """Test that a user with an invalid role is redirected to the home page."""
        self.client.login(username="unknown", password="unknownpassword")
        response = self.client.get(reverse("dashboard"))
        self.assertRedirects(response, reverse("home"))
