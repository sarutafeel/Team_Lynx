"""Tests of the sign up view."""
from django.contrib.auth.hashers import check_password
from django.test import TestCase
from django.urls import reverse
from tutorials.forms import SignUpForm
from tutorials.models import User
from tutorials.tests.helpers import LogInTester

class SignUpViewTestCase(TestCase, LogInTester):
    """Tests of the sign up view."""

    fixtures = ['tutorials/tests/fixtures/default_user.json']

    def setUp(self):
        self.url = reverse('sign_up')
        self.form_input = {
            'first_name': 'Jane',
            'last_name': 'Smith',
            'username': '@janesmith',
            'email': 'janesmith@example.org',
            'new_password': 'Password123',
            'password_confirmation': 'Password123'
        }
        self.user = User.objects.get(username='@johndoe')

    def test_sign_up_url(self):
        """Test that the URL for sign up is correct."""
        self.assertEqual(self.url, '/sign_up/')

    def test_get_sign_up(self):
        """Test accessing the sign-up page."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'sign_up.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, SignUpForm))
        self.assertFalse(form.is_bound)

    def test_get_sign_up_redirects_when_logged_in(self):
        """Test accessing sign-up when already logged in."""
        self.client.login(username=self.user.username, password="Password123")
        response = self.client.get(self.url, follow=True)
        redirect_url = reverse('student_dashboard')
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'student_dashboard.html')

    def test_unsuccesful_sign_up(self):
        """Test unsuccessful sign-up due to invalid username."""
        self.form_input['username'] = 'BAD_USERNAME'
        before_count = User.objects.count()
        response = self.client.post(self.url, self.form_input)
        after_count = User.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'sign_up.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, SignUpForm))
        self.assertTrue(form.is_bound)
        self.assertFalse(self._is_logged_in())

    def test_succesful_sign_up(self):
        """Test successful sign-up and redirection."""
        before_count = User.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        after_count = User.objects.count()

        # Check if a user was created
        self.assertEqual(after_count, before_count + 1, "User was not created after sign-up.")
        
        # Validate redirection
        response_url = reverse('student_dashboard')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'student_dashboard.html')

        # Verify user details
        try:
            user = User.objects.get(username='@janesmith')
            self.assertEqual(user.first_name, 'Jane')
            self.assertEqual(user.last_name, 'Smith')
            self.assertEqual(user.email, 'janesmith@example.org')
            is_password_correct = check_password('Password123', user.password)
            self.assertTrue(is_password_correct, "Password mismatch after creation.")
            self.assertTrue(self._is_logged_in(), "User not logged in after sign-up.")
        except User.DoesNotExist:
            self.fail("User @janedoe was not created in the database.")


    def test_post_sign_up_redirects_when_logged_in(self):
        """Test submitting sign-up form when already logged in."""
        self.client.login(username=self.user.username, password="Password123")
        before_count = User.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        after_count = User.objects.count()
        self.assertEqual(after_count, before_count)
        redirect_url = reverse('student_dashboard')
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'student_dashboard.html')
