# tutorials/tests/views/test_student_dashboard.py

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from tutorials.models import LessonSchedule, Student, Tutor
from datetime import datetime
from django.utils import timezone 


User = get_user_model()

class StudentDashboardViewTest(TestCase):

    def setUp(self):
    # Create a student user
        self.client = Client()
        self.user = User.objects.create_user(
        username="@teststudent", password="testpassword", role="student"
        )
        self.student = Student.objects.create(user=self.user)

    # Create a tutor user
        self.tutor_user = User.objects.create_user(
        username="testtutor", email="tutor@example.com", password="testpassword"
        )
        self.tutor = Tutor.objects.create(user=self.tutor_user)

        # Assign lessons to the student with a valid tutor (User instance)
        LessonSchedule.objects.create(
            student=self.student.user,
            tutor=self.tutor_user,  # Pass the User instance, not Tutor
            subject="Python",
            start_time=timezone.now(),
            duration=60,
            status="scheduled",
        )

        LessonSchedule.objects.create(
            student=self.student.user,
            tutor=self.tutor_user,  # Pass the User instance, not Tutor
            subject="C++",
            start_time=timezone.now(),
            duration=45,
            status="scheduled",
        )

        self.url = reverse("student_dashboard")


    def test_dashboard_redirects_if_not_logged_in(self):
        response = self.client.get(self.url)
        self.assertRedirects(response, f"{reverse('log_in')}?next={self.url}")

    def test_dashboard_renders_correctly_for_logged_in_student(self):
        self.client.login(username="@teststudent", password="testpassword")
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "student_dashboard.html")
        self.assertIn("lessons", response.context)

        # Check if lessons appear in context
        lessons = response.context["lessons"]
        self.assertEqual(lessons.count(), 2)
        self.assertContains(response, "Python")
        self.assertContains(response, "C++")
