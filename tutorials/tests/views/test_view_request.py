from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from tutorials.models import StudentRequest, TutorRequest


User = get_user_model()


class StudentRequestsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="student", password="password", role="student")
        self.client.login(username="student", password="password")
        self.request = StudentRequest.objects.create(
            student=self.user,
            language="English",
            day_of_week="Monday",
            difficulty="Beginner",
            status="pending",
            frequency="weekly"
        )

    def test_view_student_requests(self):
        response = self.client.get('/student/requests/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.request.language)

    def test_no_requests(self):
        StudentRequest.objects.all().delete()
        response = self.client.get('/student/requests/')
        self.assertContains(response, "No requests found.")


class TutorRequestsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="tutor", password="password", role="tutor")
        self.client.login(username="tutor", password="password")

    def test_view_tutor_requests(self):
        response = self.client.get('/tutor/requests/')
        self.assertEqual(response.status_code, 200)

    def test_no_requests(self):
        response = self.client.get('/tutor/requests/')
        self.assertContains(response, "No tutor requests available.")


class PairRequestTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin = User.objects.create_user(username="admin", password="password", role="admin")
        self.client.login(username="admin", password="password")
        self.student_request = StudentRequest.objects.create(
            student=self.admin,
            language="English",
            day_of_week="Monday",
            difficulty="Beginner",
            status="pending",
            frequency="weekly"
        )
        self.tutor_request = TutorRequest.objects.create(
            tutor=self.admin,
            languages="English",
            day_of_week="Monday",
            level_can_teach="Beginner",
            status="available"
        )

    def test_pair_request_valid(self):
        print("test pair valid reached")
        response = self.client.post(
            f'/admin/pair/{self.student_request.id}/{self.tutor_request.id}/',
            {'tutor_request_id': self.tutor_request.id, 'start_time': '10:00', 'duration': '60'}
        )
        self.assertRedirects(response, '/admin/dashboard/')
        

    def test_pair_request_invalid(self):
        print("test pair invalid reached")
        response = self.client.post(
            f'/admin/pair/{self.student_request.id}/{self.tutor_request.id}/',
            {'tutor_request_id': '', 'start_time': '', 'duration': ''}
        )
        self.assertContains(response, "Please fill all fields.")
        


class CancelStudentRequestTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="student", password="password", role="student")
        self.client.login(username="student", password="password")
        self.request = StudentRequest.objects.create(
            student=self.user,
            language="English",
            status="pending"
        )

    def test_cancel_student_request(self):
        response = self.client.get(f'/student/request/{self.request.id}/cancel/')
        self.assertRedirects(response, '/student/dashboard/')
        self.request.refresh_from_db()
        self.assertEqual(self.request.status, "Cancelled")