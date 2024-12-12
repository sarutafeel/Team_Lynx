from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from tutorials.models import Invoice, Student, Tutor

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

        # Create related models
        self.student = Student.objects.create(user=self.student_user)
        self.tutor = Tutor.objects.create(user=self.tutor_user)

        # Create an invoice
        self.invoice = Invoice.objects.create(
            student=self.student,
            tutor=self.tutor,
            amount=100.00,
            status="Unpaid"
        )

        self.url = reverse("delete_invoice", kwargs={"invoice_id": self.invoice.id})

    def test_delete_invoice_redirects_if_not_logged_in(self):
        """Test that the view redirects if the user is not logged in."""
        response = self.client.get(self.url)
        self.assertRedirects(response, f"{reverse('log_in')}?next={self.url}")

    def test_delete_invoice_accessible_by_admin(self):
        """Test that the admin can delete an invoice."""
        self.client.login(username="admin", password="adminpassword")
        response = self.client.post(self.url)
        self.assertRedirects(response, reverse("admin_dashboard"))
        self.assertFalse(Invoice.objects.filter(pk=self.invoice.id).exists())

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
        self.client.login(username="admin", password="adminpassword")
        invalid_url = reverse("delete_invoice", kwargs={"invoice_id": 999})
        response = self.client.post(invalid_url)
        self.assertEqual(response.status_code, 404)
