from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from tutorials.models import Invoice, Tutor, Student

User = get_user_model()

class AdminInvoicesViewTest(TestCase):

    def setUp(self):
        # Create admin user
        self.admin_user = User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="adminpassword"
        )

        # Create a regular user
        self.regular_user = User.objects.create_user(
            username="user",
            email="user@example.com",
            password="userpassword"
        )

        # Create students and tutors
        self.student_user = User.objects.create_user(
            username="student_user",
            email="student@example.com",
            password="password123"
        )
        self.tutor_user = User.objects.create_user(
            username="tutor_user",
            email="tutor@example.com",
            password="password123"
        )

        self.student = Student.objects.create(user=self.student_user)
        self.tutor = Tutor.objects.create(user=self.tutor_user)

        # Create invoices
        self.invoice1 = Invoice.objects.create(
            student=self.student,
            tutor=self.tutor,
            amount=150.00,
            status="unpaid",
            due_date="2024-12-31"
        )
        self.invoice2 = Invoice.objects.create(
            student=self.student,
            tutor=self.tutor,
            amount=200.00,
            status="paid",
            due_date="2024-12-25"
        )

    def test_invoices_access_denied_for_non_admin_users(self):
        self.client.login(username="user", password="userpassword")
        response = self.client.get(reverse("admin_invoices"))
        self.assertEqual(response.status_code, 302)  # Redirect to login or access denied

    def test_invoices_access_for_admin_users(self):
        self.client.login(username="admin", password="adminpassword")
        response = self.client.get(reverse("admin_invoices"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "admin_invoices.html")

    def test_invoices_list_displayed(self):
        self.client.login(username="admin", password="adminpassword")
        response = self.client.get(reverse("admin_invoices"))

        self.assertContains(response, "150.00")
        self.assertContains(response, "200.00")
        self.assertContains(response, "unpaid")
        self.assertContains(response, "paid")

        # Check the number of invoices in the context
        self.assertEqual(len(response.context["invoices"]), 2)

        # Check that the students and tutors are included in the context
        self.assertIn(self.student, response.context["students"])
        self.assertIn(self.tutor, response.context["tutors"])
