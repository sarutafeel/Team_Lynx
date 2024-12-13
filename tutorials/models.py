from django.core.validators import RegexValidator
from django.contrib.auth.models import AbstractUser
from django.db import models
from libgravatar import Gravatar
from django.db import models
from django.conf import settings


DAY_CHOICES = [
    ('monday', 'Monday'),
    ('tuesday', 'Tuesday'),
    ('wednesday', 'Wednesday'),
    ('thursday', 'Thursday'),
    ('friday', 'Friday'),
    ('saturday', 'Saturday'),
    ('sunday', 'Sunday'),
]

LEVEL_CHOICES = [
    ('beginner', 'Beginner'),
    ('intermediate', 'Intermediate'),
    ('advanced', 'Advanced'),
]

FREQUENCY_CHOICES = [
    ("weekly", "Weekly"),
    ("fortnightly", "Fortnightly"),
]

STATUS_CHOICES = [
    ("scheduled", "Scheduled"),
    ("cancelled", "Cancelled"),
]

# class Student(models.Model):
#     user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="student_profile")
#     enrollment_date = models.DateField(auto_now_add=True)

#     def __str__(self):
#         return self.user.username


class Student(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="student_profile"
    )
    enrollment_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.user.username



class Tutor(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='tutor_profile')
    subject = models.CharField(max_length=100)
    hourly_rate = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    availability = models.TextField()  # Example field to store availability
    hours_taught = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Tutor: {self.user.full_name()}"

class Invoice(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="invoices")
    tutor = models.ForeignKey(Tutor, on_delete=models.CASCADE, related_name="invoices")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=[('paid', 'Paid'), ('unpaid', 'Unpaid')], default='unpaid')
    created_at = models.DateTimeField(auto_now_add=True)
    due_date = models.DateField()

    def __str__(self):
        return f"Invoice {self.id} - {self.student.user.username} to {self.tutor.user.username}"


class Request(models.Model):
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]

    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='requests')
    type = models.CharField(max_length=100)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='low')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')
    allocated = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.type} ({self.student.username})"
    
class Feedback(models.Model):
    name = models.CharField(max_length=50)
    email = models.EmailField()
    message = models.TextField(max_length=500)
    posted = models.DateTimeField(auto_now_add=True)  

    def __str__(self):
        return f"Feedback from {self.name} at {self.posted}"
    
class LessonSchedule(models.Model):
    tutor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='tutor_schedule'
    )
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='student_schedule'
    )
    subject = models.CharField(max_length=100)
    day_of_week = models.CharField(max_length=10, choices=DAY_CHOICES, default='monday')
    start_time = models.TimeField()
    duration = models.IntegerField(help_text="Duration in minutes")
    frequency = models.CharField(
        max_length=20,
        choices=[('weekly', 'Weekly'), ('fortnightly', 'Fortnightly')]
    )
    status = models.CharField(
        max_length=20,
        choices=[('scheduled', 'Scheduled'), ('cancelled', 'Cancelled')],
        default='scheduled'
    )

    def __str__(self):
        return f"{self.subject} - {self.student} with {self.tutor}"
    
class StudentRequest(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="student_requests")
    language = models.CharField(max_length=100)
    frequency = models.CharField(max_length=20, choices=[('weekly', 'Weekly'), ('fortnightly', 'Fortnightly')])
    day_of_week = models.CharField(max_length=10, choices=DAY_CHOICES, default='monday')
    preferred_time = models.TimeField() 
    additional_details = models.TextField(blank=True, null=True)
    difficulty = models.CharField(max_length=20, choices=LEVEL_CHOICES, default='beginner')
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected'), ('cancelled', 'Cancelled')], default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Request by {self.student.full_name} for {self.language}"
    
class TutorRequest(models.Model):
    tutor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="tutor_requests")
    languages = models.CharField(max_length=200)  
    day_of_week = models.CharField(max_length=10, choices=DAY_CHOICES, default='monday')
    available_time = models.TimeField() 
    level_can_teach = models.CharField(max_length=20, choices=LEVEL_CHOICES, default='beginner')
    additional_details = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=[('available', 'Available'), ('busy', 'Busy'),('cancelled', 'Cancelled')], default='available')

    def __str__(self):
        return f"Request by {self.tutor.full_name} for teaching {self.languages}"


#Alternate Request Model
# class Request(models.Model):
#     student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='requests')
#     type = models.CharField(max_length=100)
#     priority = models.CharField(max_length=50)
#     status = models.CharField(max_length=50)
#     allocated = models.BooleanField(default=False)

#     def __str__(self):
#         return f"Request by {self.student.user.full_name()} - {self.type}"
    



class User(AbstractUser):
    """Model used for user authentication, and team member related information."""
    ROLE_CHOICES = (
        ('student', 'Student'),
        ('tutor', 'Tutor'),
        ('admin', 'Admin'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student')
    
    username = models.CharField(
        max_length=30,
        unique=True,
        validators=[RegexValidator(
            regex=r'^@\w{3,}$',
            message='Username must consist of @ followed by at least three alphanumericals'
        )]
    )
    first_name = models.CharField(max_length=50, blank=False)
    last_name = models.CharField(max_length=50, blank=False)
    email = models.EmailField(unique=True, blank=False)


    class Meta:
        """Model options."""

        ordering = ['last_name', 'first_name']

    
    def full_name(self):
        """Return a string containing the user's full name."""

        return f'{self.first_name} {self.last_name}'

    def gravatar(self, size=120):
        """Return a URL to the user's gravatar."""

        gravatar_object = Gravatar(self.email)
        gravatar_url = gravatar_object.get_image(size=size, default='mp')
        return gravatar_url

    def mini_gravatar(self):
        """Return a URL to a miniature version of the user's gravatar."""
        
        return self.gravatar(size=60)
    


