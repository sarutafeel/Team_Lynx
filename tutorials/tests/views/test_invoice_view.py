from django.test import TestCase, Client
from django.urls import reverse
from tutorials.models import Invoice, Student, Tutor, User

class CreateInvoiceViewTestCase(TestCase):
    """Unit tests for the create_invoice view."""

    def setUp(self):
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='testpassword'
        )
        # Log in the user
        self.client = Client()
        self.client.login(username='testuser', password='testpassword')

        # Create test data
        self.student = Student.objects.create(user=self.user)
        self.tutor = Tutor.objects.create(user=self.user)

        # URL for the create_invoice view
        self.url = reverse('create_invoice')  # Update 'create_invoice' with the actual name of the URL pattern

    def test_create_invoice_post_success(self):
        """Test successful POST request to create_invoice."""
        data = {
            'student': self.student.id,
            'tutor': self.tutor.id,
            'amount': '100.00',
            'due_date': '2024-12-31'
        }
        response = self.client.post(self.url, data)

        # Check that the response redirects (or the expected status code)
        self.assertEqual(response.status_code, 302)  # Assuming a redirect after success

        # Check that the invoice was created
        invoice = Invoice.objects.get(student=self.student)
        self.assertEqual(invoice.tutor, self.tutor)
        self.assertEqual(str(invoice.amount), '100.00')
        self.assertEqual(str(invoice.due_date), '2024-12-31')

    def test_create_invoice_post_missing_data(self):
        """Test POST request to create_invoice with missing data."""
        data = {
            'student': self.student.id,
            'tutor': '',  # Missing tutor
            'amount': '100.00',
            'due_date': '2024-12-31'
        }
        response = self.client.post(self.url, data)

        # Check that the response status code is 400 or form error is handled
        self.assertEqual(response.status_code, 400)  # Assuming error returns 400

        # Check that no invoice was created
        self.assertFalse(Invoice.objects.filter(student=self.student).exists())
