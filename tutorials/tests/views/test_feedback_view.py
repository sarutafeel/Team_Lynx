from django.test import TestCase
from django.urls import reverse
from django.contrib.messages import get_messages
from tutorials.models import Feedback
from django.contrib.auth import get_user_model


class FeedbackViewTest(TestCase):

    def setUp(self):
        # Create a test user and login
        self.user = get_user_model().objects.create_user(
            username="testuser", email="testuser@example.com", password="testpassword"
        )
        self.client.login(username="testuser", password="testpassword")

        self.url = reverse("submit_feedback")
        self.valid_data = {
            "name": "John Doe",
            "email": "johndoe@example.com",
            "message": "Great platform!",
        }
        self.invalid_data = {
            "name": "",
            "email": "invalidemail",
            "message": "",
        }

    def test_feedback_view_renders_correct_template(self):
        """Test that the correct template is rendered."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "feedback.html")

    def test_feedback_submission_successful(self):
        """Test successful feedback submission with authentication."""
        response = self.client.post(self.url, self.valid_data)

        # Check the response code only for redirection
        self.assertEqual(response.status_code, 302, "Expected a 302 redirect.")

        # Check feedback creation
        self.assertTrue(
            Feedback.objects.filter(email="johndoe@example.com").exists(),
            "Feedback was not saved in the database."
        )
        # Verify feedback message
        messages = list(get_messages(response.wsgi_request))
        self.assertIn("Thank you for your feedback", [str(m) for m in messages])



    def test_feedback_submission_fails(self):
        """Test feedback submission fails due to invalid data."""
        response = self.client.post(self.url, self.invalid_data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "This field is required.")
        self.assertFalse(Feedback.objects.filter(email="invalidemail").exists())

    def test_feedback_submission_missing_email(self):
        """Test feedback submission fails due to missing email."""
        response = self.client.post(self.url, {
            "name": "Jane Doe",
            "email": "",
            "message": "Missing email test"
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "This field is required.")
        self.assertFalse(Feedback.objects.filter(name="Jane Doe").exists())
