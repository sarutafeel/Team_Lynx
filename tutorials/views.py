from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ImproperlyConfigured
from django.shortcuts import redirect, render, get_object_or_404
from django.views import View
from django.views.generic.edit import FormView, UpdateView
from django.urls import reverse
from tutorials.forms import LogInForm, PasswordForm, UserForm, SignUpForm, FeedbackForm
from tutorials.helpers import login_prohibited
from tutorials.forms import TutorSignUpForm
from django.contrib.auth.decorators import user_passes_test


from .models import Request, Tutor, Invoice, Student, LessonSchedule, StudentRequest, TutorRequest, Feedback
from django.db import models
from django.db.models import Sum

from .forms import LessonScheduleForm, StudentRequestForm, TutorRequestForm
from django.http import HttpResponseRedirect, HttpResponseForbidden, HttpResponseNotFound
from datetime import date, timedelta

@login_required
def student_dashboard(request):
    student = request.user
    lessons = LessonSchedule.objects.filter(student=student).order_by('start_time')
    context = {"lessons": lessons}
    return render(request, "student_dashboard.html", context)


@login_required
def student_requests(request):
    """View student requests."""
    student = request.user
    # Query student requests
    student_requests = StudentRequest.objects.filter(student=student).order_by('-created_at')
    context = {"student_requests": student_requests}
    return render(request, "student_requests.html", context)


@login_required
def student_invoices(request):
    """View student invoices."""
    try:
        student_profile = request.user.student_profile
    except Student.DoesNotExist:
        messages.error(request, "You are not registered as a student.")
        return redirect("home")

    invoices = Invoice.objects.filter(student=student_profile).order_by("-due_date")

    context = {"invoices": invoices}
    return render(request, "student_invoices.html", context)







# @login_required
# def student_dashboard(request):
#     """Display the student's dashboard."""
#     student = request.user

#     # Query student requests
#     student_requests = StudentRequest.objects.filter(student=student).order_by('-created_at')

#     # Handle form submission for student requests
#     if request.method == "POST":
#         form = StudentRequestForm(request.POST)
#         if form.is_valid():
#             student_request = form.save(commit=False)
#             student_request.student = student
#             student_request.status = 'pending'
#             student_request.save()
#             messages.success(request, "Your request has been submitted successfully!")
#             return redirect('student_dashboard')
#     else:
#         form = StudentRequestForm()

#     # Validate student profile
#     try:
#         student_profile = request.user.student_profile  # Access the related Student instance
#     except Student.DoesNotExist:
#         messages.error(request, "You are not registered as a student.")
#         return redirect("home")  # Redirect to a fallback page if not a student

#     # Fetch invoices and lessons
#     invoices = Invoice.objects.filter(student=student_profile)
#     lessons = LessonSchedule.objects.filter(student=student).order_by('start_time')

#     # Render the dashboard
#     context = {
#         "student_requests": student_requests,
#         "student_request_form": form,
#         "invoices": invoices,
#         "lessons": lessons,
#     }

#     return render(request, "student_dashboard.html", context)







@login_required
def tutor_dashboard(request):
    """Tutor Dashboard showing allocated lessons."""
    lessons = LessonSchedule.objects.filter(tutor=request.user).order_by('start_time')
    context = {'lessons': lessons, 'tutor_name': request.user.get_full_name() }
    return render(request, 'tutor_dashboard.html', context)



@login_required
def tutor_requests(request):
    """Tutor Requests page."""
    tutor_requests = TutorRequest.objects.filter(tutor=request.user).order_by('-status')
    context = {'tutor_requests': tutor_requests}
    return render(request, 'tutor_requests.html', context)




@login_required
@user_passes_test(lambda user: user.is_superuser)
def admin_dashboard(request):
    """Admin Dashboard showing requests and lesson scheduling."""
    student_requests = StudentRequest.objects.all().order_by('status', '-created_at')
    tutor_requests = TutorRequest.objects.all()  
    lessons = LessonSchedule.objects.all().distinct().order_by('tutor', 'student', 'subject', 'start_time', 'day_of_week')  

    context = {
        'student_requests': student_requests,
        'tutor_requests': tutor_requests,
        'lessons': lessons,
    }
    return render(request, 'admin_dashboard.html', context)


@login_required
@user_passes_test(lambda user: user.is_superuser)
def admin_invoices(request):
    """Admin view for invoices."""
    tutors = Tutor.objects.select_related('user')
    invoices = Invoice.objects.select_related('student', 'tutor__user').order_by('-created_at')
    students = Student.objects.select_related('user')
    
    context = {
        'invoices': invoices,
        'students' : students,
        'tutors' : tutors
    }
    return render(request, 'admin_invoices.html', context)


@login_required
@user_passes_test(lambda user: user.is_superuser)
def admin_feedback(request):
    """Admin view for feedback."""
    feedbacks = Feedback.objects.all().order_by('-posted')  # Fetch all feedback, ordered by newest first
    context = {'feedbacks': feedbacks}
    return render(request, 'admin_feedback.html', context)


@login_required
def admin_analytics(request):
    """Admin view for analytics."""
    
    # Tutor and student data
    tutors = Tutor.objects.select_related('user')
    students = Student.objects.select_related('user')

    # Feedback analytics
    feedbacks = Feedback.objects.all().order_by('-posted')

    # Invoices analytics
    invoices = Invoice.objects.select_related('student', 'tutor__user').order_by('-created_at')
    total_revenue = invoices.aggregate(total_revenue=Sum('amount'))['total_revenue'] or 0
    monthly_revenue = invoices.filter(due_date__month=date.today().month).aggregate(
        monthly_revenue=Sum('amount'))['monthly_revenue'] or 0

    # Lesson and request analytics
    lessons = LessonSchedule.objects.all()
    pending_requests = StudentRequest.objects.filter(status='pending').count()


    # Analytics summary
    analytics = {
        "total_tutors": tutors.count(),
        "total_students": students.count(),
        "active_tutors": tutors.filter(user__is_active=True).count(),
        "active_students": students.filter(user__is_active=True).count(),
        "hours_taught": lessons.aggregate(total_hours=Sum('duration'))['total_hours'] or 0,
        "total_feedback": feedbacks.count(),
        "total_revenue": total_revenue,
        "monthly_revenue": monthly_revenue,
        "pending_requests": pending_requests,
    }

    context = {'analytics': analytics}
    return render(request, 'admin_analytics.html', context)



@login_required
def create_invoice(request):
    if request.method == "POST":
        student_id = request.POST.get("student")
        tutor_id = request.POST.get("tutor")
        amount = request.POST.get("amount")
        due_date = request.POST.get("due_date")

        # Fetch student and tutor objects
        student = get_object_or_404(Student, id=student_id)
        tutor = get_object_or_404(Tutor, id=tutor_id)

        # Create the invoice
        Invoice.objects.create(
            student=student,  # Reference the Student model instance directly
            tutor=tutor,
            amount=amount,
            due_date=due_date
        )

        messages.success(request, "Invoice created successfully!")
        return redirect('admin_dashboard')

    students = Student.objects.all()  # Ensure all students are fetched
    tutors = Tutor.objects.all()
    return render(request, "create_invoice.html", {"students": students, "tutors": tutors})


@login_required
def mark_paid(request, invoice_id):
    """Mark an invoice as paid."""
    invoice = get_object_or_404(Invoice, id=invoice_id)
    if invoice.status == 'Paid':
        invoice.status = 'Unpaid'
        messages.success(request, f"Invoice {invoice.id} marked as Unpaid.")
    else:
        invoice.status = 'Paid'
        messages.success(request, f"Invoice {invoice.id} marked as paid.")
    invoice.save()
    return redirect('admin_dashboard')


@login_required
def view_invoice(request, invoice_id):
    """View the details of an invoice."""
    invoice = get_object_or_404(Invoice, id=invoice_id)
    return render(request, 'view_invoice.html', {'invoice': invoice})




@login_prohibited
def home(request):
    """Display the application's start/home screen."""

    return render(request, 'home.html')

@login_required
def dashboard(request):
    role_redirects = {
        'admin': 'admin_dashboard',
        'tutor': 'tutor_dashboard',
        'student': 'student_dashboard',
    }
    user_role = getattr(request.user, 'role', None)
    if user_role in role_redirects:
        return redirect(role_redirects[user_role])
    else:
        messages.error(request, "Invalid user role.")
        return redirect('home')  # Redirect to a safe fallback




class LoginProhibitedMixin:
    """Mixin that redirects when a user is logged in."""

    redirect_when_logged_in_url = None

    def dispatch(self, *args, **kwargs):
        """Redirect when logged in, or dispatch as normal otherwise."""
        if self.request.user.is_authenticated:
            return self.handle_already_logged_in(*args, **kwargs)
        return super().dispatch(*args, **kwargs)

    def handle_already_logged_in(self, *args, **kwargs):
        url = self.get_redirect_when_logged_in_url()
        return redirect(url)

    def get_redirect_when_logged_in_url(self):
        """Returns the url to redirect to when not logged in."""
        if self.redirect_when_logged_in_url is None:
            raise ImproperlyConfigured(
                "LoginProhibitedMixin requires either a value for "
                "'redirect_when_logged_in_url', or an implementation for "
                "'get_redirect_when_logged_in_url()'."
            )
        else:
            return self.redirect_when_logged_in_url



# Custom decorator to enforce admin-only access
def admin_required(view_func):
    def wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(f"{reverse('log_in')}?next={request.path}")
        if request.user.role != "admin":
            return HttpResponseForbidden("You are not authorized to access this page.")
        return view_func(request, *args, **kwargs)
    return wrapped_view


@login_required
@admin_required
def delete_invoice(request, invoice_id):
    invoice = get_object_or_404(Invoice, pk=invoice_id)
    invoice.delete()
    messages.success(request, "Invoice deleted successfully.")
    return redirect("admin_dashboard")


@login_required
@admin_required
def edit_lesson(request, pk):
    lesson = get_object_or_404(LessonSchedule, pk=pk)

    # Restrict non-admin users
    if request.user.role != "admin":
        return HttpResponseForbidden("You are not authorized to access this page.")

    if request.method == "POST":
        form = LessonScheduleForm(request.POST, instance=lesson)
        if form.is_valid():
            form.save()
            messages.success(request, "Lesson updated successfully!")
            return redirect("admin_dashboard")  # Ensure proper redirection
    else:
        form = LessonScheduleForm(instance=lesson)

    return render(request, "edit_lesson.html", {"form": form, "lesson": lesson})


@login_required
def delete_lesson(request, pk):
    lesson = get_object_or_404(LessonSchedule, pk=pk)

    # Allow deletion by admin only
    if request.user.role != "admin":
        return HttpResponseForbidden("You are not authorized to delete this lesson.")
    lesson.delete()
    messages.success(request, "Lesson deleted successfully!")
    return redirect("admin_dashboard")

    
class LogInView(LoginProhibitedMixin, View):
    """Display login screen and handle user login."""

    http_method_names = ['get', 'post']
    redirect_when_logged_in_url = settings.REDIRECT_URL_WHEN_LOGGED_IN

    def get(self, request):
        """Display log in template."""

        self.next = request.GET.get('next') or ''
        return self.render()

    def post(self, request):
        """Handle the log in process."""
        form = LogInForm(request.POST)
        self.next = request.POST.get('next') or settings.REDIRECT_URL_WHEN_LOGGED_IN

        if form.is_valid():
            user = form.get_user()
            if user is not None:
                login(request, user)
                
                # Dynamically redirect based on role
                role_redirects = {
                    'admin': 'admin_dashboard',
                    'tutor': 'tutor_dashboard',
                    'student': 'student_dashboard',
                }
                return redirect(role_redirects.get(user.role, 'dashboard'))


        messages.add_message(request, messages.ERROR, "The credentials provided were invalid!")
        return self.render()


    
    def render(self):
        """Render log in template with blank log in form."""

        form = LogInForm()
        return render(self.request, 'log_in.html', {'form': form, 'next': self.next})



def log_out(request):
    """Log out the current user"""

    logout(request)
    return redirect('home')



class PasswordView(LoginRequiredMixin, FormView):
    """Display password change screen and handle password change requests."""

    template_name = 'password.html'
    form_class = PasswordForm

    def get_form_kwargs(self, **kwargs):
        """Pass the current user to the password change form."""

        kwargs = super().get_form_kwargs(**kwargs)
        kwargs.update({'user': self.request.user})
        return kwargs

    def form_valid(self, form):
        """Handle valid form by saving the new password."""

        form.save()
        login(self.request, self.request.user)
        return super().form_valid(form)

    def get_success_url(self):
        """Redirect the user after successful password change."""

        messages.add_message(self.request, messages.SUCCESS, "Password updated!")
        return reverse('dashboard')


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """Display user profile editing screen, and handle profile modifications."""

    model = UserForm
    template_name = "profile.html"
    form_class = UserForm

    def get_object(self):
        """Return the object (user) to be updated."""
        user = self.request.user
        return user

    def get_success_url(self):
        """Return redirect URL after successful update."""
        messages.add_message(self.request, messages.SUCCESS, "Profile updated!")
        return reverse(settings.REDIRECT_URL_WHEN_LOGGED_IN)


class SignUpView(LoginProhibitedMixin, FormView):
    """Display the sign up screen and handle sign ups."""

    form_class = SignUpForm
    template_name = "sign_up.html"
    redirect_when_logged_in_url = settings.REDIRECT_URL_WHEN_LOGGED_IN

    def form_valid(self, form):
        self.object = form.save()
        Student.objects.create(user=self.object)
        login(self.request, self.object)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(settings.REDIRECT_URL_WHEN_LOGGED_IN)







class TutorSignUpView(LoginProhibitedMixin, FormView):
    """View to handle tutor signups."""

    form_class = TutorSignUpForm
    template_name = "tutor_sign_up.html"
    redirect_when_logged_in_url = settings.REDIRECT_URL_WHEN_LOGGED_IN

    def form_valid(self, form):
        self.object = form.save()
        Tutor.objects.create(user=self.object)
        login(self.request, self.object)
        return super().form_valid(form)


    def get_success_url(self):
        return reverse('dashboard')
    

class FeedbackView(FormView):
    form_class = FeedbackForm
    template_name = "feedback.html"

    def form_valid(self, form):
        feedback = form.save()  # Save the feedback to the database
        print(f"Saved feedback: {feedback.name}, {feedback.email}, {feedback.message}")
        messages.success(self.request, "Thank you for your feedback")
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('dashboard')

    
@login_required
def admin_request_list(request):
    if not request.user.role == 'admin':
        return redirect('dashboard')

    student_requests = StudentRequest.objects.filter(status='pending').order_by('created_at')
    tutor_requests = TutorRequest.objects.all()  # show all tutor requests

    return render(request, 'request_list.html', {
        'student_requests': student_requests,
        'tutor_requests': tutor_requests,
    })


@login_required
def pair_request(request, student_request_id, tutor_request_id):
    if not request.user.role == 'admin':
        return redirect('dashboard')

    student_request = get_object_or_404(StudentRequest, id=student_request_id)

    if student_request.status != 'pending':
        messages.error(request, "This student request cannot be paired as it is not in 'pending' status.")
        return redirect('admin_dashboard')
    
    tutor_requests = TutorRequest.objects.filter(
        status='available',
        day_of_week=student_request.day_of_week,
        languages__icontains=student_request.language, 
        level_can_teach=student_request.difficulty
    )
    tutor_request = None
    if request.method == 'POST':
        tutor_request_id = request.POST.get('tutor_request_id')
        start_time = request.POST.get('start_time')
        duration = request.POST.get('duration') # as string
        day_of_week = student_request.day_of_week
        frequency = student_request.frequency

        if tutor_request_id and start_time and duration:
            try:
                duration = int(duration)
            except ValueError:
                messages.error(request, "Duration must be an integer.")
                return redirect('pair_request', student_request_id=student_request_id)

            tutor_request = get_object_or_404(TutorRequest, id=tutor_request_id)

            
            # create lesson schedule after pairing
            LessonSchedule.objects.create(
                tutor=tutor_request.tutor,
                student=student_request.student,
                subject=student_request.language,
                day_of_week=day_of_week,
                start_time=request.POST.get('start_time'),
                duration=duration,
                frequency=student_request.frequency,
                status='scheduled'
            )

            student_request.status = 'approved'
            student_request.save()

            tutor_request.status = 'scheduled'
            tutor_request.save()

            messages.success(request, "Student and tutor paired successfully!")
            return redirect('admin_dashboard')
        else:
            messages.error(request, "Please fill all fields.")
    

    return render(request, 'pair_request.html', {
        'student_request': student_request,
        'tutor_requests': tutor_requests,
    }) 



@login_required
def submit_student_request(request):
    if request.method == "POST":
        form = StudentRequestForm(request.POST)
        if form.is_valid():
            student_request = form.save(commit=False)
            student_request.student = request.user
            student_request.status = 'pending'
            student_request.save()
            messages.success(request, "Your request has been submitted!")
            return redirect('student_dashboard')
    else:
        form = StudentRequestForm()
    return render(request, 'submit_student_request.html', {'student_request_form': form})


@login_required
def submit_tutor_request(request):
    if request.method == "POST":
        form = TutorRequestForm(request.POST)
        if form.is_valid():
            tutor_request = form.save(commit=False)
            tutor_request.tutor = request.user
            tutor_request.status = 'available'
            tutor_request.save()
            messages.success(request, "Your availability has been submitted!")
            return redirect('tutor_dashboard')
    else:
        form = TutorRequestForm()
    return render(request, 'submit_tutor_request.html', {'tutor_request_form': form})



@login_required
def cancel_lesson(request, lesson_id):
    lesson = get_object_or_404(LessonSchedule, id=lesson_id)

    if request.user != lesson.student and request.user != lesson.tutor:
        messages.error(request, "You are not authorised to cancel this lesson.")
        return redirect('dashboard')
    if request.method == "POST":
        lesson.status = 'cancelled'
        lesson.save()

        messages.success(request, f"Lesson '{lesson.subject}' has been cancelled.")
        return redirect('dashboard')
    
    return render(request, 'cancel_lesson.html', {'lesson': lesson})


def cancel_student_request(request, request_id):
    student_request = get_object_or_404(StudentRequest, id=request_id, student=request.user)

    if student_request.status == 'pending':
        student_request.status = "Cancelled"
        student_request.save()
        messages.success(request, "Your request has been cancelled.")
    else:
        messages.error(request, "Only pending requests can be cancelled.")
    
    return redirect('student_dashboard')


def cancel_tutor_request(request, request_id):
    tutor_request = get_object_or_404(TutorRequest, id=request_id, tutor=request.user)

    if tutor_request.status == 'available':
        tutor_request.status = "Cancelled"
        tutor_request.save()
        messages.success(request, "Your request has been cancelled.")
    else:
        messages.error(request, "Only available requests can be cancelled.")
    
    return redirect('tutor_dashboard')