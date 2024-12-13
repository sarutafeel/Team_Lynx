from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from tutorials.models import TutorRequest

User = get_user_model()

class CancelTutorRequestViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Create a tutor user
        cls.tutor_user = User.objects.create_user(
            username="tutoruser", email="tutoruser@example.com", password="tutorpass", role="tutor"
        )

        # Correct fields based on the model definition
        cls.available_request = TutorRequest.objects.create(
            tutor=cls.tutor_user,
            languages="Math",
            day_of_week="monday",
            available_time="10:00:00",
            level_can_teach="beginner",
            additional_details="Available for tutoring",
            status="available",
        )

        cls.busy_request = TutorRequest.objects.create(
            tutor=cls.tutor_user,
            languages="Science",
            day_of_week="wednesday",
            available_time="11:00:00",
            level_can_teach="intermediate",
            additional_details="Currently tutoring physics",
            status="busy",
        )

        cls.cancel_url_available = reverse(
            "cancel_tutor_request", args=[cls.available_request.id]
        )
        cls.cancel_url_busy = reverse(
            "cancel_tutor_request", args=[cls.busy_request.id]
        )

    def test_redirect_if_not_logged_in(self):
        """Test that the page redirects if the user is not logged in."""
        response = self.client.get(self.cancel_url_available)
        self.assertRedirects(
            response, f"{reverse('log_in')}?next={self.cancel_url_available}"
        )

    def test_cancel_available_request(self):
        """Test that an available request is successfully cancelled."""
        self.client.login(username="tutoruser", password="tutorpass")
        response = self.client.post(self.cancel_url_available)

        self.available_request.refresh_from_db()
        self.assertRedirects(response, reverse("tutor_dashboard"))
        self.assertEqual(self.available_request.status, "Cancelled")

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), "Your request has been cancelled.")

    def test_cancel_non_available_request(self):
        """Test that a non-available request cannot be cancelled."""
        self.client.login(username="tutoruser", password="tutorpass")
        response = self.client.post(self.cancel_url_busy)

        self.busy_request.refresh_from_db()
        self.assertRedirects(response, reverse("tutor_dashboard"))
        self.assertEqual(self.busy_request.status, "busy")

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), "Only available requests can be cancelled.")

    def test_cancel_request_by_unauthorized_user(self):
        """Test that an unauthorized user cannot cancel a request."""
        other_user = User.objects.create_user(
            username="otheruser", email="otheruser@example.com", password="otherpass", role="tutor"
        )
        self.client.login(username="otheruser", password="otherpass")
        response = self.client.post(self.cancel_url_available)
        self.assertEqual(response.status_code, 404)
