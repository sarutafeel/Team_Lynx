from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from tutorials.models import LessonSchedule, Tutor, Student

User = get_user_model()

class DeleteLessonViewTest(TestCase):

    def setUp(self):
        # Create users
        self.admin_user = User.objects.create_superuser(
            username="admin", email="admin@example.com", password="adminpassword", role="admin"
        )

        self.student_user = User.objects.create_user(
            username="student", email="student@example.com", password="studentpassword", role="student"
        )

        self.tutor_user = User.objects.create_user(
            username="tutor", email="tutor@example.com", password="tutorpassword", role="tutor"
        )

        # Create related models
        self.student = Student.objects.create(user=self.student_user)
        self.tutor = Tutor.objects.create(user=self.tutor_user)

        # Create a lesson
        self.lesson = LessonSchedule.objects.create(
            student=self.student,
            tutor=self.tutor,
            subject="Math",
            start_time="10:00:00",
            day_of_week="Monday",
            duration=60
        )

        self.url = reverse("delete_lesson", kwargs={"pk": self.lesson.pk})

    def test_delete_lesson_redirects_if_not_logged_in(self):
        """Test that the view redirects if the user is not logged in."""
        response = self.client.get(self.url)
        self.assertRedirects(response, f"{reverse('log_in')}?next={self.url}")

    def test_delete_lesson_accessible_by_admin(self):
        """Test that the admin can access and delete a lesson."""
        self.client.login(username="admin", password="adminpassword")
        response = self.client.post(self.url)
        self.assertRedirects(response, reverse("admin_dashboard"))
        self.assertFalse(LessonSchedule.objects.filter(pk=self.lesson.pk).exists())

        messages = list(get_messages(response.wsgi_request))
        self.assertIn("Lesson deleted successfully!", str(messages[0]))

    def test_delete_lesson_forbidden_for_student(self):
        """Test that a student cannot delete a lesson."""
        self.client.login(username="student", password="studentpassword")
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 403)  # Forbidden

    def test_delete_lesson_forbidden_for_tutor(self):
        """Test that a tutor cannot delete a lesson."""
        self.client.login(username="tutor", password="tutorpassword")
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 403)  # Forbidden

    def test_delete_lesson_nonexistent_lesson(self):
        """Test that deleting a nonexistent lesson raises a 404."""
        self.client.login(username="admin", password="adminpassword")
        invalid_url = reverse("delete_lesson", kwargs={"pk": 999})
        response = self.client.post(invalid_url)
        self.assertEqual(response.status_code, 404)
