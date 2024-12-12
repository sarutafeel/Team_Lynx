from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from tutorials.models import Tutor, TutorRequest

User = get_user_model()

class TutorRequestsViewTest(TestCase):

    def setUp(self):
        # Create a test user and tutor profile
        self.tutor_user = User.objects.create_user(
            username="tutortest", email="tutor@example.com", password="testpassword"
        )
        self.tutor = Tutor.objects.create(user=self.tutor_user)

        # Create some tutor requests
        self.request1 = TutorRequest.objects.create(
            tutor=self.tutor_user,
            languages="Python",
            available_time="2024-12-12 10:00:00",
            additional_details="Available for weekend tutoring.",
            status="pending",
        )

        self.request2 = TutorRequest.objects.create(
            tutor=self.tutor_user,
            languages="Java",
            available_time="2024-12-15 14:00:00",
            additional_details="Looking for evening slots.",
            status="approved",
        )

    def test_requests_redirects_if_not_logged_in(self):
        """Test that unauthenticated users are redirected."""
        response = self.client.get(reverse("tutor_requests"))
        self.assertRedirects(response, f"{reverse('log_in')}?next={reverse('tutor_requests')}")

    def test_requests_renders_correctly_for_logged_in_tutor(self):
        """Test that the tutor requests page renders correctly."""
        self.client.login(username="tutortest", password="testpassword")
        response = self.client.get(reverse("tutor_requests"))

        # Check response status
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "tutor_requests.html")

        # Check context data
        self.assertIn("tutor_requests", response.context)
        tutor_requests = response.context["tutor_requests"]

        # Check the order and content of requests
        self.assertEqual(len(tutor_requests), 2)
        self.assertEqual(tutor_requests[0], self.request2)  # Approved first
        self.assertEqual(tutor_requests[1], self.request1)  # Pending next
