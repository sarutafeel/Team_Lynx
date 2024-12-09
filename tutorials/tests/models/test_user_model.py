"""Unit tests for the User model."""
from datetime import time
from django.core.exceptions import ValidationError
from django.test import TestCase
from tutorials.models import Feedback, Invoice, LessonSchedule, Request, Student, StudentRequest, Tutor, TutorRequest, User

class UserModelTestCase(TestCase):
    """Unit tests for the User model."""

    fixtures = [
        'tutorials/tests/fixtures/default_user.json',
        'tutorials/tests/fixtures/other_users.json'
    ]

    GRAVATAR_URL = "https://www.gravatar.com/avatar/363c1b0cd64dadffb867236a00e62986"

    def setUp(self):
        self.user = User.objects.get(username='@johndoe')
        self.tutor = Tutor.objects.get(id=1)
        self.student = Student.objects.get(id=1)
        self.user2 = User.objects.get(username='@janedoe')
        self.user3 = User.objects.get(username='@peterpickles')
        self.invoice = Invoice.objects.create(
            student=self.student,
            tutor=self.tutor,
            amount=100.00,
            status='unpaid',
            created_at= "2024-11-30",
            due_date="2024-12-31",
        )
        self.request = Request.objects.create(
            student=self.student.user,
            type="Python",
            priority="medium",   
            status="pending",    
            allocated=False
        )
        self.feedback = Feedback.objects.create(
            name="John Doe",
            email="johndoe@example.com",
            message="This is a test feedback message.",
        )
        self.lesson_schedule = LessonSchedule.objects.create(
            tutor=self.tutor.user,
            student=self.student.user,
            subject="Mathematics",
            day_of_week="monday",
            start_time="10:00:00",
            duration=60,
            frequency="weekly",
            status="scheduled"
        )
        self.student_request = StudentRequest.objects.create(
            student=self.student.user,
            language="Python",
            frequency="weekly",
            day_of_week="monday",
            preferred_time=time(14, 0),  
            additional_details="Looking for a tutor with native proficiency.",
            difficulty="beginner",
            status="pending"
        )
        tutor_request = TutorRequest.objects.create(
            tutor=self.tutor.user,
            languages="Python, C++",
            day_of_week="monday",
            available_time=time(10, 0),  
            level_can_teach="beginner",
            additional_details="Specializes in teaching beginers students.",
            status="available"
        )
        

    def test_valid_user(self):
        self._assert_user_is_valid()

    def test_username_cannot_be_blank(self):
        self.user.username = ''
        self._assert_user_is_invalid()

    def test_username_can_be_30_characters_long(self):
        self.user.username = '@' + 'x' * 29
        self._assert_user_is_valid()

    def test_username_cannot_be_over_30_characters_long(self):
        self.user.username = '@' + 'x' * 30
        self._assert_user_is_invalid()

    def test_username_must_be_unique(self):
        self.user.username = self.user2.username
        self._assert_user_is_invalid()

    def test_username_must_start_with_at_symbol(self):
        self.user.username = 'johndoe'
        self._assert_user_is_invalid()

    def test_username_must_contain_only_alphanumericals_after_at(self):
        self.user.username = '@john!doe'
        self._assert_user_is_invalid()

    def test_username_must_contain_at_least_3_alphanumericals_after_at(self):
        self.user.username = '@jo'
        self._assert_user_is_invalid()

    def test_username_may_contain_numbers(self):
        self.user.username = '@j0hndoe2'
        self._assert_user_is_valid()

    def test_username_must_contain_only_one_at(self):
        self.user.username = '@@johndoe'
        self._assert_user_is_invalid()

    def test_first_name_must_not_be_blank(self):
        self.user.first_name = ''
        self._assert_user_is_invalid()

    def test_first_name_need_not_be_unique(self):
        self.user.first_name = self.user2.first_name
        self._assert_user_is_valid()

    def test_first_name_may_contain_50_characters(self):
        self.user.first_name = 'x' * 50
        self._assert_user_is_valid()

    def test_first_name_must_not_contain_more_than_50_characters(self):
        self.user.first_name = 'x' * 51
        self._assert_user_is_invalid()

    def test_last_name_must_not_be_blank(self):
        self.user.last_name = ''
        self._assert_user_is_invalid()

    def test_last_name_need_not_be_unique(self):
        self.user.last_name = self.user2.last_name
        self._assert_user_is_valid()

    def test_last_name_may_contain_50_characters(self):
        self.user.last_name = 'x' * 50
        self._assert_user_is_valid()

    def test_last_name_must_not_contain_more_than_50_characters(self):
        self.user.last_name = 'x' * 51
        self._assert_user_is_invalid()

    def test_email_must_not_be_blank(self):
        self.user.email = ''
        self._assert_user_is_invalid()

    def test_email_must_be_unique(self):
        self.user.email = self.user2.email
        self._assert_user_is_invalid()

    def test_email_must_contain_username(self):
        self.user.email = '@example.org'
        self._assert_user_is_invalid()

    def test_email_must_contain_at_symbol(self):
        self.user.email = 'johndoe.example.org'
        self._assert_user_is_invalid()

    def test_email_must_contain_domain_name(self):
        self.user.email = 'johndoe@.org'
        self._assert_user_is_invalid()

    def test_email_must_contain_domain(self):
        self.user.email = 'johndoe@example'
        self._assert_user_is_invalid()

    def test_email_must_not_contain_more_than_one_at(self):
        self.user.email = 'johndoe@@example.org'
        self._assert_user_is_invalid()

    def test_full_name_must_be_correct(self):
        full_name = self.user.get_full_name()  
        self.assertEqual(full_name, "John Doe")

    def test_default_gravatar(self):
        actual_gravatar_url = self.user.gravatar()
        expected_gravatar_url = f"{self.GRAVATAR_URL}?size=120&default=mp"
        self.assertEqual(actual_gravatar_url, expected_gravatar_url)

    def test_custom_gravatar(self):
        actual_gravatar_url = self.user.gravatar(size=100)
        expected_gravatar_url = f"{self.GRAVATAR_URL}?size=100&default=mp"
        self.assertEqual(actual_gravatar_url, expected_gravatar_url)

    def test_mini_gravatar(self):
        actual_gravatar_url = self.user.mini_gravatar()
        expected_gravatar_url = f"{self.GRAVATAR_URL}?size=60&default=mp"
        self.assertEqual(actual_gravatar_url, expected_gravatar_url)

    def _assert_user_is_valid(self):
        try:
            self.user.full_clean()
        except ValidationError:
            self.fail('Test user should be valid')

    def _assert_user_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.user.full_clean()

    def test_str_student_method(self):
        expected_str = self.user3.username
        self.assertEqual(str(self.student), expected_str)

    def test_str_tutor_method(self):
        expected_str = f"Tutor: {self.user2.get_full_name()}"
        self.assertEqual(str(self.tutor), expected_str)

    def test_str_invoice_method(self):
        expected_str = f"Invoice {self.invoice.id} - {self.student.user.username} to {self.tutor.user.username}"
        self.assertEqual(str(self.invoice), expected_str)

    def test_str_request_method(self):
        expected_str = f"{self.request.type} ({self.student.user.username})"
        self.assertEqual(str(self.request), expected_str)

    def test_str_feedback_method(self):
        expected_str = f"Feedback from {self.feedback.name} at {self.feedback.posted}"
        self.assertEqual(str(self.feedback), expected_str)
    
    def test_str_lesson_schedule_method(self):
        expected_str = f"{self.lesson_schedule.subject} - {self.lesson_schedule.student} with {self.lesson_schedule.tutor}"
        self.assertEqual(str(self.lesson_schedule), expected_str)

    def test_str_student_request_method(self):
        expected_str = f"Request by {self.student_request.student.get_full_name()} for {self.student_request.language}"
        self.assertEqual(str(self.student_request), expected_str)

    def test_str_tutor_request_method(self):
        expected_str = f"Request by {self.tutor_request.tutor.user.get_full_name()} for teaching {self.tutor_request.languages}"
        self.assertEqual(str(self.tutor_request), expected_str)



