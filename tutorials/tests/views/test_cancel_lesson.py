from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.utils.timezone import now
from tutorials.models import LessonSchedule

User = get_user_model()


class CancelLessonViewTest(TestCase):

    def setUp(self):
        # Create a student and tutor
        self.student_user = User.objects.create_user(
            username="studentuser", password="studentpass", role="student"
        )
        self.tutor_user = User.objects.create_user(
            username="tutoruser", password="tutorpass", role="tutor"
        )

        # Create a lesson
        self.lesson = LessonSchedule.objects.create(
            student=self.student_user,
            tutor=self.tutor_user,
            subject="Math",
            day_of_week="Monday",
            start_time="10:00",
            duration=60,
            frequency="weekly",
            status="scheduled",
        )

        self.cancel_url = reverse("cancel_lesson", args=[self.lesson.id])

    def test_redirect_if_not_logged_in(self):
        """Test that the page redirects if the user is not logged in."""
        response = self.client.get(self.cancel_url)
        self.assertRedirects(response, f"{reverse('log_in')}?next={self.cancel_url}")

    def test_access_by_authorised_student(self):
        """Test that a student can access the cancel lesson page."""
        self.client.login(username="studentuser", password="studentpass")
        response = self.client.get(self.cancel_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "cancel_lesson.html")
        self.assertEqual(response.context["lesson"], self.lesson)

    def test_access_by_authorised_tutor(self):
        """Test that a tutor can access the cancel lesson page."""
        self.client.login(username="tutoruser", password="tutorpass")
        response = self.client.get(self.cancel_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "cancel_lesson.html")
        self.assertEqual(response.context["lesson"], self.lesson)

    def test_access_by_unauthorised_user(self):
        """Test that an unauthorised user cannot cancel a lesson."""
        unauthorised_user = User.objects.create_user(
            username="unauthoriseduser", password="unauthorisedpass"
        )
        self.client.login(username="unauthoriseduser", password="unauthorisedpass")
        response = self.client.post(self.cancel_url)
        self.assertRedirects(response, reverse("dashboard"))

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(
            str(messages[0]), "You are not authorised to cancel this lesson."
        )

    def test_cancel_lesson_as_student(self):
        """Test that a student can cancel a lesson."""
        self.client.login(username="studentuser", password="studentpass")
        response = self.client.post(self.cancel_url)
        self.lesson.refresh_from_db()

        self.assertRedirects(response, reverse("dashboard"))
        self.assertEqual(self.lesson.status, "cancelled")

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(
            str(messages[0]), f"Lesson '{self.lesson.subject}' has been cancelled."
        )

    def test_cancel_lesson_as_tutor(self):
        """Test that a tutor can cancel a lesson."""
        self.client.login(username="tutoruser", password="tutorpass")
        response = self.client.post(self.cancel_url)
        self.lesson.refresh_from_db()

        self.assertRedirects(response, reverse("dashboard"))
        self.assertEqual(self.lesson.status, "cancelled")

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(
            str(messages[0]), f"Lesson '{self.lesson.subject}' has been cancelled."
        )
