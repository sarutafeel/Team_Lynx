from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import get_user_model
from tutorials.models import Tutor, LessonSchedule, Student

User = get_user_model()

class TutorDashboardViewTest(TestCase):

    def setUp(self):
        # Create a test user and tutor profile
        self.tutor_user = User.objects.create_user(
            username="tutortest", email="tutor@example.com", password="testpassword"
        )
        self.student_user1 = User.objects.create_user(
            username="student1", email="student1@example.com", password="testpassword"
        )
        self.student_user2 = User.objects.create_user(
            username="student2", email="student2@example.com", password="testpassword"
        )

        self.tutor = Tutor.objects.create(user=self.tutor_user)
        self.student1 = Student.objects.create(user=self.student_user1)
        self.student2 = Student.objects.create(user=self.student_user2)

        # Create some lessons for the tutor
        self.lesson1 = LessonSchedule.objects.create(
            tutor=self.tutor_user,
            student=self.student_user1,
            subject="Math",
            start_time=timezone.now(),
            duration=60,
            status="scheduled",
        )

        self.lesson2 = LessonSchedule.objects.create(
            tutor=self.tutor_user,
            student=self.student_user2,
            subject="Science",
            start_time=timezone.now() + timezone.timedelta(days=1),
            duration=45,
            status="scheduled",
        )

    def test_dashboard_redirects_if_not_logged_in(self):
        """Test that unauthenticated users are redirected."""
        response = self.client.get(reverse("tutor_dashboard"))
        self.assertRedirects(response, f"{reverse('log_in')}?next={reverse('tutor_dashboard')}")

    def test_dashboard_renders_correctly_for_logged_in_tutor(self):
        """Test that the tutor dashboard renders correctly."""
        self.client.login(username="tutortest", password="testpassword")
        response = self.client.get(reverse("tutor_dashboard"))

        # Check response status
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "tutor_dashboard.html")

        # Check context data
        self.assertIn("lessons", response.context)
        self.assertIn("tutor_name", response.context)
        self.assertEqual(response.context["tutor_name"], self.tutor_user.get_full_name())

        # Check lessons in context
        lessons = response.context["lessons"]
        self.assertEqual(len(lessons), 2)
        self.assertIn(self.lesson1, lessons)
        self.assertIn(self.lesson2, lessons)
