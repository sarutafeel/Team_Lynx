from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.test import Client

User = get_user_model()

class AdminRequestListViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse("admin_request_list")

        # Create users
        self.admin_user = User.objects.create_user(
            username="admin_test",
            email="admin@test.com",
            password="adminpassword",
            role="admin",
        )

        self.student_user = User.objects.create_user(
            username="student_test",
            email="student@test.com",
            password="studentpassword",
            role="student",
        )

    def test_admin_access_request_list(self):
        """Test that admin users can access the request list."""
        self.client.login(username="admin_test", password="adminpassword")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "request_list.html")

    def test_redirect_if_not_admin(self):
        """Test that non-admin users are redirected to the login page."""
        self.client.login(username="studentuser", password="studentpassword")
        response = self.client.get(self.url)
        
        # Check redirection to login page with appropriate next URL
        expected_redirect_url = f"{reverse('log_in')}?next={self.url}"
        self.assertRedirects(response, expected_redirect_url, status_code=302, target_status_code=200)


    def test_redirect_if_not_logged_in(self):
        """Test that users are redirected if not logged in."""
        response = self.client.get(self.url)
        self.assertRedirects(
            response,
            f"{reverse('log_in')}?next={self.url}",
            status_code=302,
            target_status_code=200,
        )
