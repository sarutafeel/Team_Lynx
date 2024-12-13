from django.core.management.base import BaseCommand
from tutorials.models import User, Student, Tutor, StudentRequest, TutorRequest, LessonSchedule, Feedback
import pytz
from faker import Faker
from random import choice
from datetime import time
from random import choice, randint


user_fixtures = [
    {'username': '@johndoe', 'email': 'john.doe@example.org', 'first_name': 'John', 'last_name': 'Doe', 'role': 'admin', 'is_staff': True, 'is_superuser': True},
    {'username': '@janedoe', 'email': 'jane.doe@example.org', 'first_name': 'Jane', 'last_name': 'Doe', 'role': 'tutor'},
    {'username': '@charlie', 'email': 'charlie.johnson@example.org', 'first_name': 'Charlie', 'last_name': 'Johnson', 'role': 'student'},
]

class Command(BaseCommand):
    USER_COUNT = 300
    DEFAULT_PASSWORD = 'Password123'
    STUDENT_REQUEST_COUNT = 1000
    TUTOR_REQUEST_COUNT = 1000
    LESSON_COUNT = 500
    FEEDBACK_COUNT = 200
    BATCH_SIZE = 1000
    help = 'Seeds the database with sample data'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.faker = Faker('en_GB')

    def handle(self, *args, **options):
        existing_emails = set(User.objects.values_list('email', flat=True))
        self.generate_user_fixtures(existing_emails)
        self.generate_random_users(existing_emails)
        self.generate_student_requests()
        self.generate_tutor_requests()
        self.generate_lessons()
        self.generate_feedback()
        print("Seeding complete!")

    def create_user(self, data):
        
        user = User.objects.create_user(
            username=data['username'],
            email=data['email'],
            password=Command.DEFAULT_PASSWORD,
            first_name=data['first_name'],
            last_name=data['last_name'],
            role=data['role'],
        )
        user.is_staff = data.get('is_staff', False)
        user.is_superuser = data.get('is_superuser', False)
        user.save()

        if data['role'] == 'tutor':
            from tutorials.models import Tutor
            Tutor.objects.get_or_create(
                user=user,
                defaults={
                    'subject': 'Default Subject',
                    'hourly_rate': 30.0,
                    'availability': 'available',
                    'hours_taught': 0,
                }
            )
        elif data['role'] == 'student':
            from tutorials.models import Student
            Student.objects.get_or_create(user=user)

        return user
    def create_unique_email(self, first_name, last_name, existing_emails):
        base_email = f"{first_name.lower()}.{last_name.lower()}@example.org"
        email = base_email
        counter = 1

       
        while email in existing_emails or User.objects.filter(email=email).exists():
            email = f"{first_name.lower()}.{last_name.lower()}{counter}@example.org"
            counter += 1

        existing_emails.add(email)
        return email

    def create_unique_username(self, first_name, last_name, existing_usernames):
        base_username = f"@{first_name.lower()}{last_name.lower()}"
        username = base_username
        counter = 1

       
        while username in existing_usernames or User.objects.filter(username=username).exists():
            username = f"@{first_name.lower()}{last_name.lower()}{counter}"
            counter += 1

        existing_usernames.add(username)
        return username

    def generate_user_fixtures(self, existing_emails):
        for data in user_fixtures:
            self.try_create_user(data, existing_emails)

    def generate_random_users(self, existing_emails):
        user_count = User.objects.count()
        while user_count < self.USER_COUNT:
            print(f"Seeding user {user_count}/{self.USER_COUNT}", end='\r')
            self.generate_user(existing_emails)
            user_count = User.objects.count()
        print("User seeding complete.")

    def generate_user(self, existing_emails):
        for i in range(self.USER_COUNT):
            role = choice(['student', 'tutor'])
            first_name = self.faker.first_name()
            last_name = self.faker.last_name()
            email = f"{first_name.lower()}.{last_name.lower()}{i}@example.org"
            username = f"{first_name.lower()}_{last_name.lower()}_{i}"

           
            user = User.objects.create_user(
                username=username,
                email=email,
                password=self.DEFAULT_PASSWORD,
                first_name=first_name,
                last_name=last_name,
                role=role,
            )

          
            if role == 'student':
                Student.objects.create(user=user)
            elif role == 'tutor':
                Tutor.objects.create(
                    user=user,
                    subject=choice(['Python', 'Java', 'C++', 'Scala']),
                    hourly_rate=choice([30.0, 50.0, 70.0]),
                    availability='available',
                    hours_taught=choice(range(100))
                )
        print(f"Created {self.USER_COUNT} users")

    def try_create_user(self, data, existing_emails):
        try:
            self.create_user(data)
            existing_emails.add(data['email'])
        except Exception as e:
            print(f"Failed to create user: {e}")
    
    def generate_lessons(self):
        students = Student.objects.all()
        tutors = Tutor.objects.all()
        lessons = []

        
        scheduled_lesson_count = int(self.LESSON_COUNT * 0.5)  # only add 50% of scheduled lesson
        scheduled_lessons = 0

        for _ in range(self.LESSON_COUNT):
            student = choice(students)
            tutor = choice(tutors)

        
            status = 'scheduled' if scheduled_lessons < scheduled_lesson_count and randint(0, 1) == 1 else 'cancelled'
        
         
            lesson = LessonSchedule(
                student=student.user,
                tutor=tutor.user,
                subject=choice(['Python', 'Java', 'C++', 'Scala']),
                day_of_week=choice(['monday', 'tuesday', 'wednesday', 'thursday', 'friday']),
                start_time=self.generate_time(),
                duration=choice([30, 45, 60, 90]),
                frequency=choice(['weekly', 'fortnightly']),
                status=status
            )
            lessons.append(lesson)

            if status == 'scheduled':
                
                tutor_obj = Tutor.objects.get(user=tutor.user)
                if tutor_obj.availability != 'scheduled':  
                    tutor_obj.availability = 'scheduled'
                    tutor_obj.save()

               
                student_request = StudentRequest.objects.filter(student=student.user, status="pending").first()
                if student_request:
                    student_request.status = 'scheduled'
                    student_request.save()

                scheduled_lessons += 1

            
            if len(lessons) >= self.BATCH_SIZE:
                LessonSchedule.objects.bulk_create(lessons)
                lessons.clear()

       
        if lessons:
            LessonSchedule.objects.bulk_create(lessons)

       #for checking
        print(f"Created {self.LESSON_COUNT} lessons: {scheduled_lessons} scheduled and {self.LESSON_COUNT - scheduled_lessons} cancelled.")
   
    def update_tutor_availability(self):
        for tutor in Tutor.objects.all():
            if LessonSchedule.objects.filter(tutor=tutor.user).exists():
                tutor.availability = 'scheduled'
            else:
                tutor.availability = 'available'
            tutor.save()

    def generate_feedback(self):
       
        feedbacks = []
        all_users = User.objects.filter(role__in=['student', 'tutor'])

        for _ in range(self.FEEDBACK_COUNT):
            user = choice(all_users)
            feedbacks.append(
            Feedback(
                name=user.get_full_name(),  
                email=user.email, 
                message=self.faker.text(max_nb_chars=500),
                posted=self.faker.date_time_this_year(tzinfo=pytz.UTC),
                user=user  
            )
        )

            if len(feedbacks) >= self.BATCH_SIZE:
                Feedback.objects.bulk_create(feedbacks)
                feedbacks.clear()

        if feedbacks:
            Feedback.objects.bulk_create(feedbacks)

        print(f"Created {self.FEEDBACK_COUNT} feedback entries")

    def generate_time(self):
        hour = randint(0, 23)
        minute = choice([0, 30])  
        return time(hour=hour, minute=minute)

    def generate_student_requests(self):
        students = Student.objects.all()
        student_requests = []

        for _ in range(self.STUDENT_REQUEST_COUNT):
            student = choice(students)
            student_requests.append(
                StudentRequest(
                    student=student.user,  
                    language=choice(['Python', 'Java', 'C++', 'Scala']),
                    day_of_week=choice(['Monday', 'Tuesday', 'Wednesday']),
                    difficulty=choice(['Beginner', 'Intermediate', 'Advanced']),
                    status="pending",
                    frequency=choice(['weekly', 'fortnightly']),
                    preferred_time=self.generate_time()
                )
            )
            if len(student_requests) >= self.BATCH_SIZE:
                StudentRequest.objects.bulk_create(student_requests)
                student_requests.clear()

       
        if student_requests:
            StudentRequest.objects.bulk_create(student_requests)

        print(f"Created {self.STUDENT_REQUEST_COUNT} student requests")

    def generate_tutor_requests(self):
        tutors = Tutor.objects.all()
        tutor_requests = []

        for _ in range(self.TUTOR_REQUEST_COUNT):
            tutor = choice(tutors)
            tutor_requests.append(
                TutorRequest(
                    tutor=tutor.user,  
                    languages=choice(['Python', 'Java', 'C++', 'Scala']),
                    day_of_week=choice(['Monday', 'Tuesday', 'Wednesday']),
                    level_can_teach=choice(['Beginner', 'Intermediate', 'Advanced']),
                    status="available",
                    available_time=self.generate_time()
                )
            )
            if len(tutor_requests) >= self.BATCH_SIZE:
                TutorRequest.objects.bulk_create(tutor_requests)
                tutor_requests.clear()

       
        if tutor_requests:
            TutorRequest.objects.bulk_create(tutor_requests)

        print(f"Created {self.TUTOR_REQUEST_COUNT} tutor requests")

def create_username(first_name, last_name, existing_emails):
    email = f"{first_name}.{last_name}@example.org"
    counter = 1
    while email in existing_emails:
        email = f"{first_name}.{last_name}{counter}@example.org"
        counter += 1
    return email

def create_email(first_name, last_name, existing_emails):
    username = '@' + first_name.lower() + last_name.lower()
    counter = 1
    while username in existing_emails:
        username = f"@{first_name.lower()}{last_name.lower()}{counter}"
        counter += 1
    return username
