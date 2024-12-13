from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from tutorials.models import StudentRequest, TutorRequest, LessonSchedule

User = get_user_model()

class PairRequestViewTest(TestCase):

    def setUp(self):
        # Create users with unique emails
        self.admin_user = User.objects.create_user(
            username="adminuser", email="adminuser@example.com", password="adminpass", role="admin"
        )
        self.student_user = User.objects.create_user(
            username="studentuser", email="studentuser@example.com", password="studentpass", role="student"
        )
        self.tutor_user = User.objects.create_user(
            username="tutoruser", email="tutoruser@example.com", password="tutorpass", role="tutor"
        )

        # Create requests
        self.student_request = StudentRequest.objects.create(
            student=self.student_user, 
            language="Python", 
            status="pending", 
            day_of_week="Monday",
            difficulty="Beginner",
            preferred_time="10:00",
            frequency="weekly"
        )
        self.tutor_request = TutorRequest.objects.create(
            tutor=self.tutor_user, 
            languages="Python", 
            status="available", 
            day_of_week="Monday", 
            level_can_teach="Beginner",
            available_time="10:00"
        )

        self.url = reverse(
            "pair_request", 
            kwargs={"student_request_id": self.student_request.id, "tutor_request_id": self.tutor_request.id}
        )


    def test_redirect_if_not_logged_in(self):
        """Test that users are redirected if not logged in."""
        response = self.client.get(self.url)
        self.assertRedirects(response, f"{reverse('log_in')}?next={self.url}")


    def test_admin_access_pair_request_page(self):
        """Test that admin users can access the pair request page."""
        self.client.login(username="adminuser", password="adminpass")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "pair_request.html")

    def test_pair_request_missing_fields(self):
        """Test that pairing fails if required fields are missing."""
        self.client.login(username="adminuser", password="adminpass")

        response = self.client.post(self.url, {
            "tutor_request_id": "",
            "start_time": "10:00",
            "duration": ""
        })

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), "Please fill all fields.")
        self.assertEqual(LessonSchedule.objects.count(), 0)
    

    # Correct Test Cases for Redirects
    def test_pair_request_invalid_student_status(self):
        """Test that pairing fails if student request is not pending."""
        self.client.login(username="adminuser", password="adminpass")
        self.student_request.status = "approved"
        self.student_request.save()

        response = self.client.post(self.url, {
            "tutor_request_id": self.tutor_request.id,
            "start_time": "10:00",
            "duration": "60"
        })

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), "This student request cannot be paired as it is not in 'pending' status.")
        self.assertRedirects(response, reverse("admin_dashboard"), status_code=302)

    def test_redirect_if_not_admin(self):
        """Test that non-admin users are redirected."""
        self.client.login(username="studentuser", password="studentpass")
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse("student_dashboard"), status_code=302)

    def test_successful_pairing(self):
        """Test that pairing works correctly with valid data."""
        self.client.login(username="adminuser", password="adminpass")

        response = self.client.post(self.url, {
            "tutor_request_id": self.tutor_request.id,
            "start_time": "10:00",
            "duration": "60"
        })

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), "Student and tutor paired successfully!")
        self.assertRedirects(response, reverse("admin_dashboard"), status_code=302)

        self.student_request.refresh_from_db()
        self.tutor_request.refresh_from_db()
        lesson = LessonSchedule.objects.get()

        self.assertEqual(self.student_request.status, "approved")
        self.assertEqual(self.tutor_request.status, "scheduled")
        self.assertEqual(lesson.subject, "Python")
        self.assertEqual(str(lesson.start_time), "10:00:00")
        self.assertEqual(lesson.duration, 60)
        self.assertEqual(lesson.status, "scheduled")
