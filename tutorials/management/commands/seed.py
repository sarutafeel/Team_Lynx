from django.core.management.base import BaseCommand
from tutorials.models import User, Student, Tutor, StudentRequest, TutorRequest
import pytz
from faker import Faker

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
        print("Seeding complete!")

    def create_user(self, data):
        # Create the user# Create the user
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
                    'availability': 'Flexible',
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

        # Ensure the email is unique
        while email in existing_emails or User.objects.filter(email=email).exists():
            email = f"{first_name.lower()}.{last_name.lower()}{counter}@example.org"
            counter += 1

        existing_emails.add(email)
        return email

    def create_unique_username(self, first_name, last_name, existing_usernames):
        base_username = f"@{first_name.lower()}{last_name.lower()}"
        username = base_username
        counter = 1

        # Ensure the username is unique
        while username in existing_usernames or User.objects.filter(username=username).exists():
            username = f"@{first_name.lower()}{last_name.lower()}{counter}"
            counter += 1

        existing_usernames.add(username)
        return username

    def generate_user_fixtures(self, existing_emails):
        for data in user_fixtures:
            self.try_create_user(data)

    def generate_random_users(self):
        user_count = User.objects.count()
        while user_count < self.USER_COUNT:
            print(f"Seeding user {user_count}/{self.USER_COUNT}", end='\r')
            self.generate_user()
            user_count = User.objects.count()
        print("User seeding complete.")

    def generate_user(self, existing_emails):
        for i in range(self.USER_COUNT):
            role = choice(['student', 'tutor'])
            first_name = self.faker.first_name()
            last_name = self.faker.last_name()
            email = f"{first_name.lower()}.{last_name.lower()}{i}@example.org"
            username = f"{first_name.lower()}_{last_name.lower()}_{i}"

            # Create User
            user = User.objects.create_user(
                username=username,
                email=email,
                password=self.DEFAULT_PASSWORD,
                first_name=first_name,
                last_name=last_name,
                role=role,
            )

            # Create related Student or Tutor
            if role == 'student':
                Student.objects.create(user=user)
            elif role == 'tutor':
                Tutor.objects.create(
                    user=user,
                    subject=choice(['Python', 'Java', 'C++', 'JavaScript']),
                    hourly_rate=choice([30.0, 50.0, 70.0]),
                    availability=self.faker.text(max_nb_chars=50),
                    hours_taught=choice(range(100))
                )
        print(f"Created {self.USER_COUNT} users")

    def try_create_user(self, data):
        try:
            self.create_user(data)
        except Exception as e:
            print(f"Failed to create user: {e}")

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
                    student=student.user,  # Use related User instance
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

        # Final batch creation
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
                    tutor=tutor.user,  # Use related User instance
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

        # Final batch creation
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
