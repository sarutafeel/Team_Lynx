from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.http import HttpResponseForbidden
from django.contrib.messages import get_messages
from tutorials.models import LessonSchedule, Tutor, Student
from tutorials.forms import LessonScheduleForm

User = get_user_model()


class EditLessonViewTest(TestCase):

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

        # Create student and tutor profiles
        self.student = Student.objects.create(user=self.student_user)
        self.tutor = Tutor.objects.create(user=self.tutor_user)

        # Create a lesson
        self.lesson = LessonSchedule.objects.create(
            student=self.student_user,
            tutor=self.tutor_user,
            subject="Math",
            start_time="10:00:00",
            day_of_week="Monday",
            duration=60,
        )

        self.url = reverse("edit_lesson", kwargs={"pk": self.lesson.pk})

    def test_redirect_if_not_logged_in(self):
        """Test that unauthenticated users are redirected."""
        response = self.client.get(self.url)
        self.assertRedirects(response, f"{reverse('log_in')}?next={self.url}")

    def test_accessible_by_admin(self):
        """Test that the admin user can access the edit lesson page."""
        self.client.login(username="admin", password="adminpassword")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "edit_lesson.html")
        self.assertIsInstance(response.context["form"], LessonScheduleForm)

    def test_access_forbidden_for_student_or_tutor(self):
        """Test that students and tutors cannot access the edit lesson page."""
        self.client.login(username="student", password="studentpassword")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

        self.client.login(username="tutor", password="tutorpassword")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_lesson_update_successful(self):
        """Test that a valid form submission updates the lesson and redirects."""
        self.client.login(username="admin", password="adminpassword")
        updated_data = {
            "student": self.student_user.id,
            "tutor": self.tutor_user.id,
            "subject": "Physics",
            "start_time": "11:00:00",
            "day_of_week": "Tuesday",
            "duration": 90,
        }
        response = self.client.post(self.url, data=updated_data)
        self.assertRedirects(response, reverse("admin_dashboard"))

        # Verify the update
        self.lesson.refresh_from_db()
        self.assertEqual(self.lesson.subject, "Physics")
        self.assertEqual(self.lesson.start_time, "11:00:00")
        self.assertEqual(self.lesson.day_of_week, "Tuesday")
        self.assertEqual(self.lesson.duration, 90)

    def test_form_errors_displayed(self):
        """Test that form errors are displayed correctly."""
        self.client.login(username="admin", password="adminpassword")
        invalid_data = {
            "student": "",  # Missing student
            "tutor": self.tutor_user.id,
            "subject": "",
            "start_time": "25:00:00",  # Invalid time
            "day_of_week": "InvalidDay",
            "duration": "abc",  # Invalid duration
        }
        response = self.client.post(self.url, data=invalid_data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "This field is required")
        self.assertContains(response, "Enter a valid time")
        self.assertContains(response, "Select a valid choice")

    def test_success_message_on_update(self):
        """Test that a success message is displayed after a successful update."""
        self.client.login(username="admin", password="adminpassword")
        updated_data = {
            "student": self.student_user.id,
            "tutor": self.tutor_user.id,
            "subject": "Physics",
            "start_time": "11:00:00",
            "day_of_week": "Tuesday",
            "duration": 90,
        }
        response = self.client.post(self.url, data=updated_data, follow=True)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Lesson updated successfully!")
