from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from tutorials.models import TutorRequest

User = get_user_model()


class CancelTutorRequestViewTest(TestCase):

    def setUp(self):
        # Create a tutor user
        self.tutor_user = User.objects.create_user(
            username="tutoruser", password="tutorpass", role="tutor"
        )

        # Create available and scheduled requests
        self.available_request = TutorRequest.objects.create(
            tutor=self.tutor_user,
            languages="Math",
            day_of_week="Monday",
            level_can_teach="Beginner",
            available_time="10:00",
            additional_details="Can teach algebra",
            status="available",
        )

        self.scheduled_request = TutorRequest.objects.create(
            tutor=self.tutor_user,
            languages="Science",
            day_of_week="Wednesday",
            level_can_teach="Advanced",
            available_time="11:00",
            additional_details="Can teach physics",
            status="scheduled",
        )

        self.cancel_url_available = reverse(
            "cancel_tutor_request", args=[self.available_request.id]
        )
        self.cancel_url_scheduled = reverse(
            "cancel_tutor_request", args=[self.scheduled_request.id]
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
        response = self.client.post(self.cancel_url_scheduled)

        self.scheduled_request.refresh_from_db()
        self.assertRedirects(response, reverse("tutor_dashboard"))
        self.assertEqual(self.scheduled_request.status, "scheduled")

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), "Only available requests can be cancelled.")

    def test_cancel_request_by_unauthorized_user(self):
        """Test that an unauthorized user cannot cancel a request."""
        other_user = User.objects.create_user(
            username="otheruser", password="otherpass", role="tutor"
        )
        self.client.login(username="otheruser", password="otherpass")
        response = self.client.post(self.cancel_url_available)
        self.assertEqual(response.status_code, 404)
