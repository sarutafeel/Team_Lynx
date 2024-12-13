from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from tutorials.models import StudentRequest

User = get_user_model()


class CancelStudentRequestViewTest(TestCase):

    def setUp(self):
        # Create a student user
        self.student_user = User.objects.create_user(
            username="studentuser", password="studentpass", role="student"
        )

        # Create pending and approved requests
        self.pending_request = StudentRequest.objects.create(
            student=self.student_user,
            language="Math",
            frequency="weekly",
            day_of_week="Monday",
            preferred_time="10:00",
            additional_details="Need help with algebra",
            status="pending",
        )

        self.approved_request = StudentRequest.objects.create(
            student=self.student_user,
            language="Science",
            frequency="weekly",
            day_of_week="Wednesday",
            preferred_time="11:00",
            additional_details="Need help with physics",
            status="approved",
        )

        self.cancel_url_pending = reverse(
            "cancel_student_request", args=[self.pending_request.id]
        )
        self.cancel_url_approved = reverse(
            "cancel_student_request", args=[self.approved_request.id]
        )

    def test_redirect_if_not_logged_in(self):
        """Test that the page redirects if the user is not logged in."""
        response = self.client.get(self.cancel_url_pending)
        self.assertRedirects(
            response, f"{reverse('log_in')}?next={self.cancel_url_pending}"
        )

    def test_cancel_pending_request(self):
        """Test that a pending request is successfully cancelled."""
        self.client.login(username="studentuser", password="studentpass")
        response = self.client.post(self.cancel_url_pending)

        self.pending_request.refresh_from_db()
        self.assertRedirects(response, reverse("student_dashboard"))
        self.assertEqual(self.pending_request.status, "Cancelled")

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), "Your request has been cancelled.")

    def test_cancel_non_pending_request(self):
        """Test that a non-pending request cannot be cancelled."""
        self.client.login(username="studentuser", password="studentpass")
        response = self.client.post(self.cancel_url_approved)

        self.approved_request.refresh_from_db()
        self.assertRedirects(response, reverse("student_dashboard"))
        self.assertEqual(self.approved_request.status, "approved")

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), "Only pending requests can be cancelled.")

    def test_cancel_request_by_unauthorized_user(self):
        """Test that an unauthorized user cannot cancel a request."""
        other_user = User.objects.create_user(
            username="otheruser", password="otherpass", role="student"
        )
        self.client.login(username="otheruser", password="otherpass")
        response = self.client.post(self.cancel_url_pending)
        self.assertEqual(response.status_code, 404)
