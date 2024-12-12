from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from tutorials.models import Invoice, Student, Tutor

User = get_user_model()

class ViewInvoiceTest(TestCase):

    def setUp(self):
        # Create an admin user
        self.admin_user = User.objects.create_superuser(
            username="admin", email="admin@example.com", password="adminpassword"
        )

        # Create sample student and tutor
        self.student_user = User.objects.create_user(
            username="student1", email="student1@example.com", password="studentpassword"
        )
        self.tutor_user = User.objects.create_user(
            username="tutor1", email="tutor1@example.com", password="tutorpassword"
        )

        self.student = Student.objects.create(user=self.student_user)
        self.tutor = Tutor.objects.create(user=self.tutor_user)

        # Create a sample invoice
        self.invoice = Invoice.objects.create(
            student=self.student, tutor=self.tutor, amount=150.00, status="Unpaid"
        )

    def test_view_invoice_redirects_if_not_logged_in(self):
        """Test that viewing an invoice redirects if not logged in."""
        response = self.client.get(reverse("view_invoice", args=[self.invoice.id]))
        self.assertRedirects(
            response, f"{reverse('log_in')}?next={reverse('view_invoice', args=[self.invoice.id])}"
        )

    def test_view_invoice_as_authenticated_user(self):
        """Test viewing an invoice when logged in."""
        self.client.login(username="admin", password="adminpassword")
        response = self.client.get(reverse("view_invoice", args=[self.invoice.id]))

        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "view_invoice.html")
        self.assertContains(response, "150.00")
        self.assertContains(response, "Unpaid")
        self.assertContains(response, self.student.user.username)
        self.assertContains(response, self.tutor.user.username)

    def test_view_invalid_invoice(self):
        """Test viewing a non-existent invoice returns a 404."""
        self.client.login(username="admin", password="adminpassword")
        response = self.client.get(reverse("view_invoice", args=[999]))
        self.assertEqual(response.status_code, 404)