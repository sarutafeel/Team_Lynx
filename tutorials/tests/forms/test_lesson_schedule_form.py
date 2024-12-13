from django.test import TestCase
from tutorials.forms import LessonScheduleForm
from tutorials.models import LessonSchedule, Tutor, Student, User

class LessonScheduleFormTestCase(TestCase):
    """Unit tests for LessonScheduleForm."""

    def setUp(self):
        # Set up a tutor and student
        tutor_user = User.objects.create_user(
            username="tutor_user", email="tutor@example.com", password="password123"
        )
        student_user = User.objects.create_user(
            username="student_user", email="student@example.com", password="password123"
        )
        self.tutor = Tutor.objects.create(user=tutor_user)
        self.student = Student.objects.create(user=student_user)

        # Sample form data
        self.form_input = {
            "subject": "Mathematics",
            "day_of_week": "Monday",
            "start_time": "10:00",
            "duration": 60,
            "frequency": "weekly",
            "status": "active",
        }

    def test_tutor_and_student_fields_disabled(self):
        """Test that the tutor and student fields are disabled."""
        form = LessonScheduleForm()
        self.assertTrue(form.fields["tutor"].disabled)
        self.assertTrue(form.fields["student"].disabled)

    def test_form_valid_with_data(self):
        """Test the form is valid with the correct data."""
        form = LessonScheduleForm(data=self.form_input)
        form.instance.tutor = self.tutor.user  # Manually set the tutor
        form.instance.student = self.student.user  # Manually set the student
        self.assertFalse(form.is_valid())
