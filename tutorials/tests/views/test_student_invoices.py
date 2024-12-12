# tutorials/tests/views/test_student_invoices.py

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from tutorials.models import Student, Invoice, Tutor
from datetime import date, timedelta

User = get_user_model()


class StudentInvoicesViewTest(TestCase):

    def setUp(self):
        # Set up client and users
        self.client = Client()
        self.student_user = User.objects.create_user(
            username="@teststudent", password="testpassword", role="student"
        )
        self.student_profile = Student.objects.create(user=self.student_user)

        self.tutor_user = User.objects.create_user(
            username="@testtutor", password="testpassword", role="tutor"
        )
        self.tutor_profile = Tutor.objects.create(
            user=self.tutor_user, subject="Math", hourly_rate=50.00, availability="MWF"
        )

        # Create sample invoices
        self.invoice1 = Invoice.objects.create(
            student=self.student_profile,
            tutor=self.tutor_profile,
            amount=200.00,
            status="unpaid",
            due_date=date.today() + timedelta(days=7),
        )

        self.invoice2 = Invoice.objects.create(
            student=self.student_profile,
            tutor=self.tutor_profile,
            amount=150.00,
            status="paid",
            due_date=date.today() - timedelta(days=7),
        )

        self.url = reverse("student_invoices")

    def test_student_invoices_redirects_if_not_logged_in(self):
        response = self.client.get(self.url)
        self.assertRedirects(response, f"{reverse('log_in')}?next={self.url}")

    def test_student_invoices_error_if_not_registered_student(self):
        # Create a non-student user
        non_student_user = User.objects.create_user(
            username="@notstudent", password="testpassword", role="tutor"
        )

        self.client.login(username="@notstudent", password="testpassword")
        response = self.client.get(self.url)

        # Check messages for error
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "You are not registered as a student.")
        self.assertRedirects(response, reverse("home"))

    def test_student_invoices_renders_correctly_for_logged_in_student(self):
        self.client.login(username="@teststudent", password="testpassword")
        response = self.client.get(self.url)

        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "student_invoices.html")
        self.assertIn("invoices", response.context)

        # Check invoices appear in context
        invoices = response.context["invoices"]
        self.assertEqual(invoices.count(), 2)

        # Ensure the invoices appear in the rendered template
        self.assertContains(response, "200.00")
        self.assertContains(response, "150.00")
        self.assertContains(response, "unpaid")
        self.assertContains(response, "paid")
