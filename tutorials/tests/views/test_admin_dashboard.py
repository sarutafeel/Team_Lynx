from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from tutorials.models import (
    Student, Tutor, StudentRequest, TutorRequest, LessonSchedule
)

User = get_user_model()

class AdminDashboardViewTest(TestCase):

    def setUp(self):
        # Create an admin user
        self.admin_user = User.objects.create_superuser(
            username="admin", email="admin@example.com", password="adminpassword"
        )

        # Create related student and tutor users
        self.student_user = User.objects.create_user(
            username="student", email="student@example.com", password="testpassword"
        )
        self.student = Student.objects.create(user=self.student_user)

        self.tutor_user = User.objects.create_user(
            username="tutor", email="tutor@example.com", password="testpassword"
        )
        self.tutor = Tutor.objects.create(user=self.tutor_user)

        # Create test data
        self.student_request = StudentRequest.objects.create(
            student=self.student_user,
            language="Python",
            frequency="Weekly",
            day_of_week="Monday",
            preferred_time="10:00",
            status="pending",
        )

        self.tutor_request = TutorRequest.objects.create(
            tutor=self.tutor_user,
            languages="Python, JavaScript",
            available_time="2024-12-12 10:00:00",
            additional_details="Evenings only.",
            status="available",
        )

        self.lesson = LessonSchedule.objects.create(
            tutor=self.tutor_user,
            student=self.student_user,
            subject="Python",
            day_of_week="Monday",
            start_time="14:00",
            duration=60,
            status="scheduled",
        )

    def test_dashboard_redirects_if_not_logged_in(self):
        """Test that unauthenticated users are redirected to login."""
        response = self.client.get(reverse("admin_dashboard"))
        self.assertRedirects(
            response, f"{reverse('log_in')}?next={reverse('admin_dashboard')}"
        )

    def test_dashboard_renders_correctly_for_logged_in_admin(self):
        """Test that the admin dashboard renders correctly for admins."""
        self.client.login(username="admin", password="adminpassword")
        response = self.client.get(reverse("admin_dashboard"))

        # Verify status and template
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "admin_dashboard.html")

        # Verify context data
        self.assertIn("student_requests", response.context)
        self.assertIn("tutor_requests", response.context)
        self.assertIn("lessons", response.context)

        # Check query results
        student_requests = response.context["student_requests"]
        tutor_requests = response.context["tutor_requests"]
        lessons = response.context["lessons"]

        # Validate request contents
        self.assertEqual(student_requests.count(), 1)
        self.assertEqual(student_requests.first(), self.student_request)

        self.assertEqual(tutor_requests.count(), 1)
        self.assertEqual(tutor_requests.first(), self.tutor_request)

        self.assertEqual(lessons.count(), 1)
        self.assertEqual(lessons.first(), self.lesson)

    def test_dashboard_access_denied_for_non_admin_users(self):
        """Test that non-admin users cannot access the admin dashboard."""
        # Log in as a regular student user
        self.client.login(username="student", password="testpassword")
        response = self.client.get(reverse("admin_dashboard"))
        self.assertEqual(response.status_code, 403)  # Forbidden

        # Log in as a regular tutor user
        self.client.login(username="tutor", password="testpassword")
        response = self.client.get(reverse("admin_dashboard"))
        self.assertEqual(response.status_code, 403)
