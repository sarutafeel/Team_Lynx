from django.test import TestCase
from django.urls import reverse
from django.contrib.messages import get_messages
from tutorials.models import Feedback


class FeedbackViewTest(TestCase):

    def setUp(self):
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
        """Test successful feedback submission."""
        response = self.client.post(self.url, self.valid_data)
        self.assertRedirects(response, reverse("dashboard"))
        self.assertTrue(Feedback.objects.filter(email="johndoe@example.com").exists())

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), "Thank you for your feedback")

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
