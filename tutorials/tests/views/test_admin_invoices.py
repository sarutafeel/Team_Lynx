from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from tutorials.models import Student, Tutor, Invoice

User = get_user_model()


class AdminInvoicesViewTest(TestCase):

    def setUp(self):
        # Create admin user
        self.admin_user = User.objects.create_superuser(
            username="admin", email="admin@example.com", password="adminpassword"
        )

        # Create a student and tutor
        self.student_user = User.objects.create_user(
            username="student", email="student@example.com", password="studentpassword"
        )
        self.student = Student.objects.create(user=self.student_user)

        self.tutor_user = User.objects.create_user(
            username="tutor", email="tutor@example.com", password="tutorpassword"
        )
        self.tutor = Tutor.objects.create(user=self.tutor_user)

        # Create an invoice
        self.invoice = Invoice.objects.create(
            student=self.student,
            tutor=self.tutor,
            amount=200,
            status="unpaid",
        )

    def test_invoices_redirects_if_not_logged_in(self):
        """Test that unauthenticated users are redirected to login."""
        response = self.client.get(reverse("admin_invoices"))
        self.assertRedirects(
            response, f"{reverse('log_in')}?next={reverse('admin_invoices')}"
        )

    def test_invoices_renders_correctly_for_admin(self):
        """Test that the invoices page renders correctly for admin users."""
        self.client.login(username="admin", password="adminpassword")
        response = self.client.get(reverse("admin_invoices"))

        # Check correct response and template
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "admin_invoices.html")

        # Check context data
        self.assertIn("invoices", response.context)
        self.assertIn("students", response.context)
        self.assertIn("tutors", response.context)

        # Validate invoice data
        invoices = response.context["invoices"]
        students = response.context["students"]
        tutors = response.context["tutors"]

        self.assertEqual(invoices.count(), 1)
        self.assertEqual(students.count(), 1)
        self.assertEqual(tutors.count(), 1)

        self.assertEqual(invoices.first(), self.invoice)

    def test_invoices_access_denied_for_non_admin_users(self):
        """Test that non-admin users cannot access the invoices page."""
        # Login as a student user
        self.client.login(username="student", password="studentpassword")
        response = self.client.get(reverse("admin_invoices"))
        self.assertEqual(response.status_code, 403)  # Forbidden

        # Login as a tutor user
        self.client.login(username="tutor", password="tutorpassword")
        response = self.client.get(reverse("admin_invoices"))
        self.assertEqual(response.status_code, 403)
