from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from tutorials.models import StudentRequest, TutorRequest

User = get_user_model()


class AdminRequestListViewTest(TestCase):

    def setUp(self):
        # Create users
        self.admin_user = User.objects.create_user(
            username="adminuser", password="adminpass", role="admin"
        )
        self.student_user = User.objects.create_user(
            username="studentuser", password="studentpass", role="student"
        )

        # Create requests
        self.student_request = StudentRequest.objects.create(
            student=self.student_user, language="Python", status="pending"
        )
        self.tutor_request = TutorRequest.objects.create(
            tutor=self.admin_user, languages="Python"
        )

        self.url = reverse("admin_request_list")

    def test_redirect_if_not_logged_in(self):
        """Test that users are redirected if not logged in."""
        response = self.client.get(self.url)
        self.assertRedirects(response, f"{reverse('log_in')}?next={self.url}")

    def test_redirect_if_not_admin(self):
        """Test that non-admin users are redirected."""
        self.client.login(username="studentuser", password="studentpass")
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse("dashboard"))

    def test_admin_access_request_list(self):
        """Test that admin users can access the request list."""
        self.client.login(username="adminuser", password="adminpass")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "request_list.html")

    def test_student_requests_display(self):
        """Test that student requests are displayed correctly."""
        self.client.login(username="adminuser", password="adminpass")
        response = self.client.get(self.url)
        self.assertContains(response, self.student_request.language)
        self.assertContains(response, self.student_request.status)

    def test_tutor_requests_display(self):
        """Test that tutor requests are displayed correctly."""
        self.client.login(username="adminuser", password="adminpass")
        response = self.client.get(self.url)
        self.assertContains(response, self.tutor_request.languages)
