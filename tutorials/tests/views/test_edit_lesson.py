from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from tutorials.models import LessonSchedule, Tutor, Student
from tutorials.forms import LessonScheduleForm

User = get_user_model()


class EditLessonViewTest(TestCase):

    def setUp(self):
        # Create admin user
        self.admin_user = User.objects.create_superuser(
            username="admin", email="admin@example.com", password="adminpassword", role="admin"
        )

        # Create student and tutor
        self.student_user = User.objects.create_user(
            username="student", email="student@example.com", password="studentpassword", role="student"
        )
        self.tutor_user = User.objects.create_user(
            username="tutor", email="tutor@example.com", password="tutorpassword", role="tutor"
        )

        self.student = Student.objects.create(user=self.student_user)
        self.tutor = Tutor.objects.create(user=self.tutor_user)

        # Create a lesson to edit
        self.lesson = LessonSchedule.objects.create(
            student=self.student,
            tutor=self.tutor,
            subject="Math",
            start_time="10:00:00",
            day_of_week="Monday",
            duration=60
        )

        self.url = reverse("edit_lesson", kwargs={"pk": self.lesson.pk})

    def test_edit_lesson_redirects_if_not_logged_in(self):
        """Test that the view redirects if the user is not logged in."""
        response = self.client.get(self.url)
        self.assertRedirects(response, f"{reverse('log_in')}?next={self.url}")

    def test_edit_lesson_accessible_by_admin(self):
        """Test that the admin user can access the edit lesson page."""
        self.client.login(username="admin", password="adminpassword")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "edit_lesson.html")

    def test_edit_lesson_not_accessible_by_student_or_tutor(self):
        """Test that students and tutors cannot access the edit lesson page."""
        self.client.login(username="student", password="studentpassword")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)  # Forbidden

        self.client.login(username="tutor", password="tutorpassword")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)  # Forbidden

    def test_edit_lesson_updates_correctly(self):
        """Test that a valid form submission updates the lesson."""
        self.client.login(username="admin", password="adminpassword")
        updated_data = {
            "student": self.student.id,
            "tutor": self.tutor.id,
            "subject": "Physics",
            "start_time": "11:00:00",
            "day_of_week": "Tuesday",
            "duration": 90
        }
        response = self.client.post(self.url, data=updated_data)
        self.assertRedirects(response, reverse("admin_dashboard"))

        # Verify the update
        self.lesson.refresh_from_db()
        self.assertEqual(self.lesson.subject, "Physics")
        self.assertEqual(self.lesson.start_time, "11:00:00")
        self.assertEqual(self.lesson.day_of_week, "Tuesday")
        self.assertEqual(self.lesson.duration, 90)

    def test_edit_lesson_invalid_form(self):
        """Test that an invalid form submission doesn't update the lesson."""
        self.client.login(username="admin", password="adminpassword")
        invalid_data = {
            "student": "",  # Missing required field
            "tutor": self.tutor.id,
            "subject": "",
            "start_time": "25:00:00",  # Invalid time
            "day_of_week": "InvalidDay",
            "duration": "abc"  # Invalid duration
        }
        response = self.client.post(self.url, data=invalid_data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "This field is required.")

    def test_edit_lesson_correct_context(self):
        """Test that the correct context is passed to the template."""
        self.client.login(username="admin", password="adminpassword")
        response = self.client.get(self.url)
        self.assertIsInstance(response.context["form"], LessonScheduleForm)
