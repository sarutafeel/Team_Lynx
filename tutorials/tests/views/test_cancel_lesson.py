from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from tutorials.models import LessonSchedule

User = get_user_model()

class CancelLessonViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create users
        cls.tutor_user = User.objects.create_user(
            username="tutoruser", email="tutor@example.com", password="tutorpass", role="tutor"
        )
        cls.student_user = User.objects.create_user(
            username="studentuser", email="student@example.com", password="studentpass", role="student"
        )
        cls.other_user = User.objects.create_user(
            username="otheruser", email="other@example.com", password="otherpass", role="student"
        )

        # Create lesson
        cls.lesson = LessonSchedule.objects.create(
            tutor=cls.tutor_user,
            student=cls.student_user,
            subject="Math",
            day_of_week="monday",
            start_time="10:00",
            duration=60,
            frequency="weekly",
            status="scheduled"
        )

    def setUp(self):
        self.url = reverse("cancel_lesson", kwargs={"lesson_id": self.lesson.id})

    def test_access_by_authorised_student(self):
        self.client.login(username="studentuser", password="studentpass")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_access_by_authorised_tutor(self):
        self.client.login(username="tutoruser", password="tutorpass")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_access_by_unauthorised_user(self):
        self.client.login(username="otheruser", password="otherpass")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_cancel_lesson_as_student(self):
        self.client.login(username="studentuser", password="studentpass")
        response = self.client.post(self.url, follow=True)
        self.lesson.refresh_from_db()
        self.assertEqual(self.lesson.status, "cancelled")
        self.assertRedirects(response, reverse("student_dashboard"))

    def test_cancel_lesson_as_tutor(self):
        self.client.login(username="tutoruser", password="tutorpass")
        response = self.client.post(self.url, follow=True)
        self.lesson.refresh_from_db()
        self.assertEqual(self.lesson.status, "cancelled")
        self.assertRedirects(response, reverse("tutor_dashboard"))

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(self.url)
        login_url = f"{reverse('log_in')}?next={self.url}"
        self.assertRedirects(response, login_url)
