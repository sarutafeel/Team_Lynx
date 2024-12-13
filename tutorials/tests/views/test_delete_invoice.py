from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from tutorials.models import Invoice, Student, Tutor
from django.contrib.auth import get_user_model

User = get_user_model()


class DeleteInvoiceViewTest(TestCase):
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

        # Create Student and Tutor instances
        self.student = Student.objects.create(user=self.student_user)
        self.tutor = Tutor.objects.create(user=self.tutor_user)

        # Create Invoice
        self.invoice = Invoice.objects.create(
            student=self.student,
            tutor=self.tutor,
            amount=100.00,
            status="unpaid",
            due_date=timezone.now().date() + timezone.timedelta(days=7)
        )

        self.url = reverse("delete_invoice", kwargs={"invoice_id": self.invoice.pk})

    def test_delete_invoice_accessible_by_admin(self):
        """Test that the admin can delete an invoice."""
        self.client.login(username="admin", password="adminpassword")
        response = self.client.post(self.url)
        self.assertRedirects(response, reverse("admin_dashboard"))
        self.assertFalse(Invoice.objects.filter(pk=self.invoice.pk).exists())

    def test_delete_invoice_forbidden_for_student(self):
        """Test that a student cannot delete an invoice."""
        self.client.login(username="student", password="studentpassword")
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 403)

    def test_delete_invoice_forbidden_for_tutor(self):
        """Test that a tutor cannot delete an invoice."""
        self.client.login(username="tutor", password="tutorpassword")
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 403)

    def test_delete_invoice_nonexistent_invoice(self):
        """Test that deleting a nonexistent invoice raises a 404."""
        nonexistent_url = reverse("delete_invoice", kwargs={"invoice_id": 99999})
        self.client.login(username="admin", password="adminpassword")
        response = self.client.post(nonexistent_url)
        self.assertEqual(response.status_code, 404)

    def test_delete_invoice_redirects_if_not_logged_in(self):
        """Test that the view redirects if the user is not logged in."""
        response = self.client.post(self.url)
        self.assertRedirects(
            response, f"{reverse('log_in')}?next={self.url}", status_code=302, target_status_code=200
        )

