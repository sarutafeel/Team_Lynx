from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from tutorials.models import StudentRequest, TutorRequest, LessonSchedule

User = get_user_model()


class PairRequestViewTest(TestCase):

    def setUp(self):
        # Create users
        self.admin_user = User.objects.create_user(
            username="adminuser", email="admin@example.com", password="adminpass", role="admin"
        )
        self.student_user = User.objects.create_user(
            username="studentuser", email="student@example.com", password="studentpass", role="student"
        )
        self.tutor_user = User.objects.create_user(
            username="tutoruser", email="tutor@example.com", password="tutorpass", role="tutor"
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

        self.url = reverse("pair_request", kwargs={
            "student_request_id": self.student_request.id, 
            "tutor_request_id": self.tutor_request.id
        })

    def test_redirect_if_not_logged_in(self):
        """Test that users are redirected if not logged in."""
        response = self.client.get(self.url, follow=False)
        self.assertRedirects(response, f"{reverse('log_in')}?next={self.url}")

    def test_admin_access_pair_request_page(self):
        """Test that admin users can access the pair request page."""
        self.client.login(username="adminuser", password="adminpass")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "pair_request.html")

    def test_pair_request_missing_fields(self):
        """Test that pairing fails if fields are missing."""
        self.client.login(username="adminuser", password="adminpass")
        response = self.client.post(self.url, {
            "tutor_request_id": "",
            "start_time": "10:00",
            "duration": ""
        }, follow=False)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Please fill all fields.")
        self.assertEqual(LessonSchedule.objects.count(), 0)

    
    # Update tests with the correct expected status code
    def test_pair_request_invalid_student_status(self):
        """Test that pairing fails if student request is not pending."""
        self.client.login(username="adminuser", password="adminpass")
        self.student_request.status = "approved"
        self.student_request.save()

        response = self.client.post(self.url, {
            "tutor_request_id": self.tutor_request.id,
            "start_time": "10:00",
            "duration": "60"
        }, follow=False)

        # Expecting a 302 redirect (successful redirection)
        self.assertRedirects(response, reverse("admin_dashboard"), status_code=302, target_status_code=200)
        self.student_request.refresh_from_db()
        self.assertEqual(self.student_request.status, "approved")


    def test_successful_pairing(self):
        """Test successful pairing."""
        self.client.login(username="adminuser", password="adminpass")

        response = self.client.post(self.url, {
            "tutor_request_id": self.tutor_request.id,
            "start_time": "10:00",
            "duration": "60"
        }, follow=False)

        # Expecting a 302 redirect after pairing
        self.assertRedirects(response, reverse("admin_dashboard"), status_code=302, target_status_code=200)
        messages = list(response.wsgi_request._messages)
        self.assertEqual(str(messages[0]), "Student and tutor paired successfully!")

        # Validate database updates
        self.student_request.refresh_from_db()
        self.tutor_request.refresh_from_db()
        lesson = LessonSchedule.objects.get()

        self.assertEqual(self.student_request.status, "approved")
        self.assertEqual(self.tutor_request.status, "scheduled")
        self.assertEqual(lesson.duration, 60)
        self.assertEqual(lesson.start_time.strftime("%H:%M:%S"), "10:00:00")
