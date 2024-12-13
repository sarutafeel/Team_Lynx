# tutorials/tests/views/test_student_dashboard.py

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from tutorials.models import LessonSchedule, Student, Tutor
from django.utils import timezone

User = get_user_model()

class StudentDashboardViewTest(TestCase):

    def setUp(self):
        self.client = Client()

        # Create a student user
        self.user = User.objects.create_user(
            username="@teststudent", password="testpassword", role="student"
        )
        self.student = Student.objects.create(user=self.user)

        # Create a tutor user
        self.tutor_user = User.objects.create_user(
            username="testtutor", email="tutor@example.com", password="testpassword", role="tutor"
        )
        self.tutor = Tutor.objects.create(user=self.tutor_user)

        # Create lessons
        LessonSchedule.objects.create(
            student=self.student.user,
            tutor=self.tutor_user,
            subject="Python",
            start_time=timezone.now(),
            duration=60,
            frequency="weekly",
            status="scheduled",
        )

        LessonSchedule.objects.create(
            student=self.student.user,
            tutor=self.tutor_user,
            subject="C++",
            start_time=timezone.now(),
            duration=45,
            frequency="fortnightly",
            status="scheduled",
        )

        self.url = reverse("student_dashboard")

    def test_dashboard_redirects_if_not_logged_in(self):
        """Ensure the dashboard redirects if the user is not logged in."""
        response = self.client.get(self.url)
        self.assertRedirects(response, f"{reverse('log_in')}?next={self.url}")

    def test_dashboard_renders_correctly_for_logged_in_student(self):
        """Ensure the dashboard renders correctly when logged in."""
        self.client.login(username="@teststudent", password="testpassword")
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "student_dashboard.html")
        self.assertIn("lessons", response.context)

        # Check lessons in context
        lessons = response.context["lessons"]
        self.assertEqual(lessons.count(), 2)
        self.assertContains(response, "Python")
        self.assertContains(response, "C++")
