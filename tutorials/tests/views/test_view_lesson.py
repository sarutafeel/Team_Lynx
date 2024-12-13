from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from tutorials.models import StudentRequest, LessonSchedule

User = get_user_model()

class EditLessonTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin = User.objects.create_user(username="admin", password="password", role="admin")
        self.client.login(username="admin", password="password")
        self.lesson = LessonSchedule.objects.create(
            tutor=self.admin,
            student=self.admin,
            subject="Math",
            day_of_week="Monday",
            start_time="10:00",
            duration=60
        )

    def test_edit_lesson_valid(self):
        response = self.client.post(
            f'/admin/lesson/{self.lesson.id}/edit/',
            {
                'subject': "Science",
                'day_of_week': "Tuesday",
                'start_time': "11:00",
                'duration': 90
            }
        )
        self.assertRedirects(response, '/admin_dashboard/')
        self.lesson.refresh_from_db()
        self.assertEqual(self.lesson.subject, "Science")
        print("test edit lesson valid reached")

    def test_edit_lesson_invalid(self):
        print("test edit lesson invali")

        response = self.client.post(
            f'/admin/lesson/{self.lesson.id}/edit/',
            {
                'subject': "",  # Missing subject
                'day_of_week': "",  # Missing day_of_week
                'start_time': "",  # Missing start_time
                'duration': ""  # Missing duration
            }
        )
        self.assertContains(response, "This field is required.")
        
class DeleteLessonTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin = User.objects.create_user(username="admin", password="password", role="admin")
        self.client.login(username="admin", password="password")
        self.lesson = LessonSchedule.objects.create(
            tutor=self.admin,
            student=self.admin,
            subject="Math",
            day_of_week="Monday",
            start_time="10:00",
            duration=60
        )

    def test_delete_lesson(self):
        response = self.client.post(f'/admin/lesson/{self.lesson.id}/delete/')
        self.assertRedirects(response, '/admin/dashboard/')
        self.assertFalse(LessonSchedule.objects.filter(id=self.lesson.id).exists())

class CancelLessonTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="student", password="password", role="student")
        self.client.login(username="student", password="password")
        self.lesson = LessonSchedule.objects.create(
            tutor=self.user,
            student=self.user,
            subject="Math",
            day_of_week="Monday",
            start_time="10:00",
            duration=60,
            status="scheduled"
        )

    def test_cancel_lesson(self):
        response = self.client.post(f'/lesson/{self.lesson.id}/cancel/')
        self.assertRedirects(response, '/dashboard/')
        self.lesson.refresh_from_db()
        self.assertEqual(self.lesson.status, "cancelled")