from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from tutorials.models import Invoice, Student, Tutor

User = get_user_model()

class MarkPaidViewTest(TestCase):

    def setUp(self):
        # Create an admin user
        self.admin_user = User.objects.create_superuser(
            username="admin", email="admin@example.com", password="adminpassword"
        )

        # Create sample student and tutor
        self.student = Student.objects.create(
            user=User.objects.create_user(
                username="student1", email="student1@example.com", password="studentpassword"
            )
        )
        self.tutor = Tutor.objects.create(
            user=User.objects.create_user(
                username="tutor1", email="tutor1@example.com", password="tutorpassword"
            )
        )

        # Create a sample invoice
        self.invoice = Invoice.objects.create(
            student=self.student, tutor=self.tutor, amount=100.00, status="Unpaid"
        )

    def test_mark_paid_redirects_if_not_logged_in(self):
        """Test that marking an invoice redirects if not logged in."""
        response = self.client.get(reverse("mark_paid", args=[self.invoice.id]))
        self.assertRedirects(
            response, f"{reverse('log_in')}?next={reverse('mark_paid', args=[self.invoice.id])}"
        )

    def test_mark_invoice_as_paid(self):
        """Test marking an unpaid invoice as paid."""
        self.client.login(username="admin", password="adminpassword")
        response = self.client.get(reverse("mark_paid", args=[self.invoice.id]))

        # Refresh the invoice
        self.invoice.refresh_from_db()

        self.assertEqual(self.invoice.status, "Paid")
        self.assertRedirects(response, reverse("admin_dashboard"))

        # Check success message
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), f"Invoice {self.invoice.id} marked as paid.")

    def test_mark_invoice_as_unpaid(self):
        """Test marking a paid invoice as unpaid."""
        self.invoice.status = "Paid"
        self.invoice.save()

        self.client.login(username="admin", password="adminpassword")
        response = self.client.get(reverse("mark_paid", args=[self.invoice.id]))

        # Refresh the invoice
        self.invoice.refresh_from_db()

        self.assertEqual(self.invoice.status, "Unpaid")
        self.assertRedirects(response, reverse("admin_dashboard"))

        # Check success message
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), f"Invoice {self.invoice.id} marked as Unpaid.")

    def test_invalid_invoice_id(self):
        """Test handling of an invalid invoice ID."""
        self.client.login(username="admin", password="adminpassword")
        response = self.client.get(reverse("mark_paid", args=[999]))

        # Check that the response is 404
        self.assertEqual(response.status_code, 404)
