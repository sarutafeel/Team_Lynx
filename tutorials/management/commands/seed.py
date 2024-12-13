from django.core.management.base import BaseCommand
from tutorials.models import User
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
    help = 'Seeds the database with sample data'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.faker = Faker('en_GB')

    def handle(self, *args, **options):
        self.generate_user_fixtures()
        self.generate_random_users()
        print("Seeding complete!")

    def create_user(self, data):
        # Create the user
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

    def generate_user_fixtures(self):
        for data in user_fixtures:
            self.try_create_user(data)

    def generate_random_users(self):
        user_count = User.objects.count()
        while user_count < self.USER_COUNT:
            print(f"Seeding user {user_count}/{self.USER_COUNT}", end='\r')
            self.generate_user()
            user_count = User.objects.count()
        print("User seeding complete.")

    def generate_user(self):
        first_name = self.faker.first_name()
        last_name = self.faker.last_name()
        email = create_email(first_name, last_name)
        username = create_username(first_name, last_name)
        role = 'student'  # Default role for random users
        self.try_create_user({
            'username': username,
            'email': email,
            'first_name': first_name,
            'last_name': last_name,
            'role': role,
        })

    def try_create_user(self, data):
        try:
            self.create_user(data)
        except Exception as e:
            print(f"Failed to create user: {e}")

def create_username(first_name, last_name):
    return '@' + first_name.lower() + last_name.lower()

def create_email(first_name, last_name):
    return f"{first_name}.{last_name}@example.org"