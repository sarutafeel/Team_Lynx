from django.test import TestCase
from django.contrib.auth import get_user_model
from tutorials.models import Student, Tutor, Invoice
from datetime import date

User = get_user_model()

class StudentInvoicesViewTest(TestCase):
    def setUp(self):
        # Ensure unique emails and usernames
        self.student_user = User.objects.create_user(
            username="student_test",
            email="student_test@example.com",
            password="testpass123",
            role="student",
        )

        self.tutor_user = User.objects.create_user(
            username="tutor_test",
            email="tutor_test@example.com",
            password="testpass123",
            role="tutor",
        )

        self.student = Student.objects.create(user=self.student_user)
        self.tutor = Tutor.objects.create(user=self.tutor_user)

        # Fix: Add a due_date
        Invoice.objects.create(
            student=self.student,
            tutor=self.tutor,
            amount=100.0,
            status="unpaid",
            due_date=date.today()  # Add the required due_date
        )

    def test_student_invoices_redirects_if_not_logged_in(self):
        self.client.logout()
        response = self.client.get("/student/invoices/")
        self.assertRedirects(response, "/log_in/?next=/student/invoices/")

    def test_student_invoices_renders_correctly_for_logged_in_student(self):
        self.client.login(username="student_test", password="testpass123")
        response = self.client.get("/student/invoices/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "unpaid")
        self.assertTemplateUsed(response, "student_invoices.html")
