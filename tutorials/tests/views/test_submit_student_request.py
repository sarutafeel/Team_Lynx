from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from tutorials.models import StudentRequest
from tutorials.forms import StudentRequestForm

User = get_user_model()


class SubmitStudentRequestViewTest(TestCase):
    
    def setUp(self):
        # Create a student user
        self.student_user = User.objects.create_user(
            username="studentuser", password="studentpass", role="student"
        )
        self.url = reverse("submit_student_request")

    def test_redirect_if_not_logged_in(self):
        """Test that users are redirected if not logged in."""
        response = self.client.get(self.url)
        self.assertRedirects(response, f"{reverse('log_in')}?next={self.url}")

    def test_access_page_as_logged_in_student(self):
        """Test that the page is accessible for logged-in students."""
        self.client.login(username="studentuser", password="studentpass")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "submit_student_request.html")
        self.assertIsInstance(response.context["student_request_form"], StudentRequestForm)

    def test_form_submission_valid_data(self):
        """Test that a valid form submission creates a new StudentRequest."""
        self.client.login(username="studentuser", password="studentpass")

        data = {
            "language": "Python",
            "day_of_week": "monday",  # Lowercase for consistency
            "preferred_time": "10:00",
            "difficulty": "beginner",  # Lowercase for match
            "frequency": "weekly",     # Lowercase for match
            "additional_details": "Looking for a tutor with experience.",
        }

        response = self.client.post(self.url, data, follow=True)

        # Check success message
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), "Your request has been submitted!")

        # Verify the StudentRequest creation
        self.assertEqual(StudentRequest.objects.count(), 1)
        student_request = StudentRequest.objects.first()
        self.assertEqual(student_request.student, self.student_user)
        self.assertEqual(student_request.language, "Python")
        self.assertEqual(student_request.status, "pending")
        self.assertEqual(student_request.difficulty, "beginner")

        # Check correct template and page content
        self.assertTemplateUsed(response, "student_dashboard.html")
        self.assertContains(response, "Your request has been submitted!")

    def test_form_submission_invalid_data(self):
        """Test that invalid form data returns the same page with errors."""
        self.client.login(username="studentuser", password="studentpass")

        data = {
            "language": "",  # Missing required field
            "day_of_week": "monday",
            "preferred_time": "10:00",
            "difficulty": "beginner",
        }

        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "submit_student_request.html")
        self.assertFormError(
            response, "student_request_form", "language", "This field is required."
        )
        self.assertEqual(StudentRequest.objects.count(), 0)
