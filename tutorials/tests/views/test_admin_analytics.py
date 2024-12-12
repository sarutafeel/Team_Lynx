from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from tutorials.models import Tutor, Student, Feedback, Invoice, LessonSchedule, StudentRequest
from datetime import date
from django.utils.timezone import now
from django.db.models import Sum

User = get_user_model()

class AdminAnalyticsViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin_user = User.objects.create_user(
            username='adminuser', email='admin@example.com', password='adminpass', role='admin'
        )
        self.client.login(username='adminuser', password='adminpass')
        self.url = reverse('admin_analytics')

        # Create test data
        self.tutor_user = User.objects.create_user(
            username='tutor1', email='tutor1@example.com', password='tutorpass', role='tutor'
        )
        self.student_user = User.objects.create_user(
            username='student1', email='student1@example.com', password='studentpass', role='student'
        )

        Tutor.objects.create(user=self.tutor_user)
        Student.objects.create(user=self.student_user)

        Invoice.objects.create(
            student=Student.objects.first(),
            tutor=Tutor.objects.first(),
            amount=500,
            due_date=date.today()
        )

        Feedback.objects.create(
            name="Test Student",
            email="student1@example.com",
            message="Great service!"
        )

        LessonSchedule.objects.create(
            tutor=self.tutor_user,
            student=self.student_user,
            subject="Math",
            day_of_week="Monday",
            start_time="10:00:00",
            duration=60,
            frequency="Weekly",
            status="scheduled",
        )

        StudentRequest.objects.create(
            student=self.student_user,
            language="Math",
            day_of_week="Monday",
            difficulty="Beginner",
            status="pending",
            preferred_time="10:00:00",
        )

    def test_admin_analytics_redirects_if_not_logged_in(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertRedirects(response, f'/log_in/?next={self.url}')

    def test_admin_analytics_renders_correctly_for_logged_in_admin(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin_analytics.html')
        self.assertIn('analytics', response.context)

    def test_admin_analytics_correct_data(self):
        response = self.client.get(self.url)
        analytics = response.context['analytics']

        self.assertEqual(analytics['total_tutors'], 1)
        self.assertEqual(analytics['total_students'], 1)
        self.assertEqual(analytics['active_tutors'], 1)
        self.assertEqual(analytics['active_students'], 1)
        self.assertEqual(analytics['total_feedback'], 1)
        self.assertEqual(analytics['total_revenue'], 500)
        self.assertEqual(analytics['monthly_revenue'], 500)
        self.assertEqual(analytics['pending_requests'], 1)
        self.assertEqual(analytics['hours_taught'], 60)

    def test_admin_analytics_data_with_no_records(self):
        Invoice.objects.all().delete()
        Feedback.objects.all().delete()
        LessonSchedule.objects.all().delete()
        StudentRequest.objects.all().delete()

        response = self.client.get(self.url)
        analytics = response.context['analytics']

        self.assertEqual(analytics['total_tutors'], 1)
        self.assertEqual(analytics['total_students'], 1)
        self.assertEqual(analytics['active_tutors'], 1)
        self.assertEqual(analytics['active_students'], 1)
        self.assertEqual(analytics['total_feedback'], 0)
        self.assertEqual(analytics['total_revenue'], 0)
        self.assertEqual(analytics['monthly_revenue'], 0)
        self.assertEqual(analytics['pending_requests'], 0)
        self.assertEqual(analytics['hours_taught'], 0)
