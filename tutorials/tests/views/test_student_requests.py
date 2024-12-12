# tutorials/tests/views/test_student_requests.py

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from tutorials.models import Student, StudentRequest
from datetime import datetime

User = get_user_model()


class StudentRequestsViewTest(TestCase):

    def setUp(self):
        # Create a student user
        self.client = Client()
        self.user = User.objects.create_user(
            username="@teststudent", password="testpassword", role="student"
        )
        self.student = Student.objects.create(user=self.user)

        # Create student requests
        StudentRequest.objects.create(
            student=self.user,
            language="Python",
            frequency="Weekly",
            day_of_week="Monday",
            preferred_time="10:00 AM",
            additional_details="Need help with Django.",
            status="pending",
            created_at=datetime.now(),
        )

        StudentRequest.objects.create(
            student=self.user,
            language="JavaScript",
            frequency="Monthly",
            day_of_week="Wednesday",
            preferred_time="2:00 PM",
            additional_details="Need help with React.",
            status="approved",
            created_at=datetime.now(),
        )

        self.url = reverse("student_requests")

    def test_student_requests_redirects_if_not_logged_in(self):
        response = self.client.get(self.url)
        self.assertRedirects(response, f"{reverse('log_in')}?next={self.url}")

    def test_student_requests_renders_correctly_for_logged_in_student(self):
        self.client.login(username="@teststudent", password="testpassword")
        response = self.client.get(self.url)

        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "student_requests.html")
        self.assertIn("student_requests", response.context)

        # Check if requests appear in context
        student_requests = response.context["student_requests"]
        self.assertEqual(student_requests.count(), 2)

        # Ensure the content appears in the rendered template
        self.assertContains(response, "Python")
        self.assertContains(response, "JavaScript")
        self.assertContains(response, "Need help with Django.")
        self.assertContains(response, "Need help with React.")
