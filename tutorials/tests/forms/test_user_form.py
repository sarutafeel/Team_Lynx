"""Unit tests of the user form."""
from django import forms
from django.test import TestCase
from tutorials.forms import UserForm
from tutorials.models import User

class UserFormTestCase(TestCase):
    """Unit tests of the user form."""

    fixtures = [
        'tutorials/tests/fixtures/default_user.json'
    ]

    def setUp(self):
        """Set up valid input data for user form tests."""
        # Fetch the existing user from the fixture
        self.existing_user = User.objects.get(username='@janedoe')

        # Prepare form input data that matches the fixture
        self.form_input = {
            'first_name': self.existing_user.first_name,  # Keep first name as Jane
            'last_name': self.existing_user.last_name,    # Keep last name as Doe
            'username': self.existing_user.username,      # Use fixture's username
            'email': self.existing_user.email,            # Use fixture's email
        }

    def test_form_has_necessary_fields(self):
        """Ensure the form includes the required fields."""
        form = UserForm()
        self.assertIn('first_name', form.fields)
        self.assertIn('last_name', form.fields)
        self.assertIn('username', form.fields)
        self.assertIn('email', form.fields)
        email_field = form.fields['email']
        self.assertTrue(isinstance(email_field, forms.EmailField))

    def test_valid_user_form(self):
        """Test the form is valid with correct data."""
        form = UserForm(data=self.form_input, instance=self.existing_user)
        self.assertTrue(form.is_valid(), msg=f"Form errors: {form.errors}")

    def test_form_uses_model_validation(self):
        """Test model validation for invalid username."""
        self.form_input['username'] = 'invalid_username'
        form = UserForm(data=self.form_input, instance=self.existing_user)
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)  # Check that the error is related to the username

    def test_form_must_save_correctly(self):
        """Test the form saves data correctly."""
        form = UserForm(instance=self.existing_user, data=self.form_input)
        self.assertTrue(form.is_valid(), msg=f"Form errors: {form.errors}")  # Log errors if form is invalid
        before_count = User.objects.count()
        form.save()  # Save the form
        after_count = User.objects.count()
        self.assertEqual(after_count, before_count)  # Count should not increase
        user = User.objects.get(username='@janedoe')  # Fetch the updated user
        self.assertEqual(user.first_name, 'Jane')  # Verify the first name is still Jane
        self.assertEqual(user.last_name, 'Doe')    # Verify the last name is still Doe
        self.assertEqual(user.email, self.existing_user.email)  # Verify the email remains the same
