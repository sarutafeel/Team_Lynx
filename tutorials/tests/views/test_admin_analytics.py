from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.db.models import Sum
from tutorials.models import Tutor, Student, Feedback

User = get_user_model()

class AdminAnalyticsViewTest(TestCase):

    def setUp(self):
        # Create an admin user
        self.admin_user = User.objects.create_superuser(
            username="admin", email="admin@example.com", password="adminpassword"
        )

        # Create sample tutors, students, and feedback
        self.tutor1 = Tutor.objects.create(user=User.objects.create_user(
            username="tutor1", email="tutor1@example.com", password="tutorpassword1"
        ), hours_taught=10)

        self.tutor2 = Tutor.objects.create(user=User.objects.create_user(
            username="tutor2", email="tutor2@example.com", password="tutorpassword2"
        ), hours_taught=5)

        self.student1 = Student.objects.create(user=User.objects.create_user(
            username="student1", email="student1@example.com", password="studentpassword1"
        ))

        self.student2 = Student.objects.create(user=User.objects.create_user(
            username="student2", email="student2@example.com", password="studentpassword2"
        ))

        Feedback.objects.create(
            name="John Doe",
            email="john@example.com",
            message="Great platform!",
        )

        Feedback.objects.create(
            name="Jane Doe",
            email="jane@example.com",
            message="Needs improvement!",
        )

    def test_analytics_redirects_if_not_logged_in(self):
        """Test that unauthenticated users are redirected to login."""
        response = self.client.get(reverse("admin_analytics"))
        self.assertRedirects(
            response, f"{reverse('log_in')}?next={reverse('admin_analytics')}"
        )

    def test_analytics_renders_correctly_for_admin(self):
        """Test that analytics data is rendered correctly for admin users."""
        self.client.login(username="admin", password="adminpassword")
        response = self.client.get(reverse("admin_analytics"))

        # Check the response and template
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "admin_analytics.html")

        # Verify analytics data
        analytics = response.context["analytics"]
        self.assertEqual(analytics["total_tutors"], 2)
        self.assertEqual(analytics["total_students"], 2)
        self.assertEqual(analytics["hours_taught"], 15)
        self.assertEqual(analytics["total_feedback"], 2)

    def test_analytics_access_denied_for_non_admin_users(self):
        """Test that non-admin users cannot access the analytics page."""
        # Create and log in as a regular student
        student_user = User.objects.create_user(
            username="student", email="student@example.com", password="studentpassword"
        )
        self.client.login(username="student", password="studentpassword")
        response = self.client.get(reverse("admin_analytics"))
        self.assertEqual(response.status_code, 403)  # Forbidden
