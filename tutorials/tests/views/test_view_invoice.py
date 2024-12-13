from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from tutorials.models import Invoice, Student, Tutor
from datetime import date

User = get_user_model()

class ViewInvoiceTest(TestCase):

    def setUp(self):
        # Create users
        self.student_user = User.objects.create_user(
            username="student", email="student@example.com", password="studentpassword", role="student"
        )
        self.tutor_user = User.objects.create_user(
            username="tutor", email="tutor@example.com", password="tutorpassword", role="tutor"
        )

        # Create related models
        self.student = Student.objects.create(user=self.student_user)
        self.tutor = Tutor.objects.create(user=self.tutor_user)

        # Create an invoice with a valid due_date
        self.invoice = Invoice.objects.create(
            student=self.student,
            tutor=self.tutor,
            amount=100.00,
            status="unpaid",
            due_date=date.today()
        )

        self.url = reverse("view_invoice", kwargs={"invoice_id": self.invoice.id})
        self.invalid_url = reverse("view_invoice", kwargs={"invoice_id": 9999})

    def test_view_invoice_as_authenticated_user(self):
        """Test viewing an invoice when logged in."""
        self.client.login(username="student", password="studentpassword")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "view_invoice.html")

    def test_view_invalid_invoice(self):
        """Test viewing a non-existent invoice returns a 404."""
        self.client.login(username="student", password="studentpassword")
        response = self.client.get(self.invalid_url)
        self.assertEqual(response.status_code, 404)

    def test_view_invoice_redirects_if_not_logged_in(self):
        """Test that viewing an invoice redirects if not logged in."""
        response = self.client.get(self.url)
        self.assertRedirects(
            response, f"{reverse('log_in')}?next={self.url}", status_code=302, target_status_code=200
        )
