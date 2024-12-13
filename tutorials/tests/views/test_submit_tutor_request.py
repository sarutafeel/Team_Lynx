from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from tutorials.models import TutorRequest
from tutorials.forms import TutorRequestForm

User = get_user_model()


class SubmitTutorRequestViewTest(TestCase):
    
    def setUp(self):
        # Create a tutor user
        self.tutor_user = User.objects.create_user(
            username="tutoruser", password="tutorpass", role="tutor"
        )
        self.url = reverse("submit_tutor_request")

    def test_redirect_if_not_logged_in(self):
        """Test that the page redirects if the user is not logged in."""
        response = self.client.get(self.url)
        self.assertRedirects(response, f"{reverse('log_in')}?next={self.url}")

    def test_access_page_as_logged_in_tutor(self):
        """Test that the page is accessible for logged-in tutors."""
        self.client.login(username="tutoruser", password="tutorpass")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "submit_tutor_request.html")
        self.assertIsInstance(response.context["tutor_request_form"], TutorRequestForm)

    def test_form_submission_valid_data(self):
        """Test that a valid form submission creates a new TutorRequest."""
        self.client.login(username="tutoruser", password="tutorpass")

        data = {
            "languages": "Python, Java",
            "day_of_week": "Monday",
            "available_time": "10:00",
            "level_can_teach": "Beginner",
            "additional_details": "Available for project guidance.",
        }

        response = self.client.post(self.url, data)
        self.assertRedirects(response, reverse("tutor_dashboard"))

        # Verify that the TutorRequest was created
        self.assertEqual(TutorRequest.objects.count(), 1)
        request = TutorRequest.objects.first()

        self.assertEqual(request.tutor, self.tutor_user)
        self.assertEqual(request.languages, "Python, Java")
        self.assertEqual(request.status, "available")
        self.assertEqual(request.level_can_teach, "Beginner")

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), "Your availability has been submitted!")

    def test_form_submission_invalid_data(self):
        """Test that invalid form submission returns the form with errors."""
        self.client.login(username="tutoruser", password="tutorpass")

        data = {
            "languages": "",  # Missing required field
            "day_of_week": "Monday",
            "available_time": "10:00",
        }

        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "submit_tutor_request.html")
        self.assertFormError(
            response, "tutor_request_form", "languages", "This field is required."
        )
        self.assertEqual(TutorRequest.objects.count(), 0)

    
        
