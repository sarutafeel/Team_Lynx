from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from tutorials.models import Student, Tutor, Invoice

User = get_user_model()

class CreateInvoiceViewTest(TestCase):
    
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

        self.valid_invoice_data = {
            "student": self.student.id,
            "tutor": self.tutor.id,
            "amount": "150.00",
            "due_date": "2024-12-31",
        }

    def test_create_invoice_redirects_if_not_logged_in(self):
        """Test that the create invoice page redirects if not logged in."""
        response = self.client.get(reverse("create_invoice"))
        self.assertRedirects(
            response, f"{reverse('log_in')}?next={reverse('create_invoice')}"
        )

    def test_create_invoice_page_renders_correctly(self):
        """Test that the create invoice page renders correctly for admin users."""
        self.client.login(username="admin", password="adminpassword")
        response = self.client.get(reverse("create_invoice"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "create_invoice.html")
        self.assertContains(response, "Create Invoice")
        self.assertContains(response, self.student.user.get_full_name())
        self.assertContains(response, self.tutor.user.get_full_name())

    def test_create_invoice_post_valid_data(self):
        """Test creating an invoice with valid data."""
        self.client.login(username="admin", password="adminpassword")
        response = self.client.post(reverse("create_invoice"), self.valid_invoice_data)

        # Check redirection
        self.assertRedirects(response, reverse("admin_dashboard"))

        # Check the invoice exists
        invoice = Invoice.objects.get(student=self.student, tutor=self.tutor)
        self.assertEqual(invoice.amount, float(self.valid_invoice_data["amount"]))
        self.assertEqual(str(invoice.due_date), self.valid_invoice_data["due_date"])

    def test_create_invoice_invalid_data(self):
        """Test creating an invoice with missing data."""
        self.client.login(username="admin", password="adminpassword")

        # Post incomplete data
        response = self.client.post(
            reverse("create_invoice"), {
                "student": self.student.id,
                "amount": "100.00",
            }
        )

        # Check the page re-renders
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "create_invoice.html")
        self.assertContains(response, "Create Invoice")

        # Check that no invoices were created
        self.assertEqual(Invoice.objects.count(), 0)
