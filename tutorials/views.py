from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpResponse #for placeholder
from django.shortcuts import redirect, render, get_object_or_404
from django.views import View
from django.views.generic.edit import FormView, UpdateView
from django.urls import reverse
from tutorials.forms import LogInForm, PasswordForm, UserForm, SignUpForm
from tutorials.helpers import login_prohibited
from django.utils.timezone import now
from datetime import datetime, timedelta
from .models import LessonSchedule
from .models import LessonRequest
from .forms import LessonScheduleForm
from django.forms import ModelForm


@login_required
def dashboard(request):
    """Display the current user's dashboard."""

    current_user = request.user
    return render(request, 'dashboard.html', {'user': current_user})


@login_prohibited
def home(request):
    """Display the application's start/home screen."""

    return render(request, 'home.html')

@login_required
def student_dashboard(request):
    requests = LessonRequest.objects.filter(student=request.user)
    schedules = LessonSchedule.objects.filter(student=request.user)
    #return render(request, 'student/dashboard.html', {'requests': requests, 'schedules': schedules})
    return HttpResponse("This is the student dashboard placeholder.")

@login_required
def tutor_dashboard(request):
    schedules = LessonSchedule.objects.filter(tutor=request.user)
    return HttpResponse("This is the tutor dashboard placeholder.")
    #return render(request, 'tutor/dashboard.html', {'schedules': schedules})

@login_required
def admin_dashboard(request):
    return HttpResponse("This is the admin dashboard placeholder.")
    #return render(request, 'admin/dashboard.html')

@login_required
def add_lesson(request):
    """Allow admins to add a new lesson manually."""
    if request.method == 'POST':
        form = LessonScheduleForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Lesson scheduled successfully!")
            return redirect('lesson_list')
    else:
        form = LessonScheduleForm()

    return render(request, 'admin/add_lesson.html', {'form': form})


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


class LogInView(LoginProhibitedMixin, View):
    """Display login screen and handle user login."""

    http_method_names = ['get', 'post']
    redirect_when_logged_in_url = settings.REDIRECT_URL_WHEN_LOGGED_IN

    def get(self, request):
        """Display log in template."""

        self.next = request.GET.get('next') or ''
        return self.render()

    def post(self, request):
        """Handle log in attempt."""

        form = LogInForm(request.POST)
        self.next = request.POST.get('next') or settings.REDIRECT_URL_WHEN_LOGGED_IN
        if form.is_valid():
            user = form.get_user()
            print(f"User logged in: {user.username}, Role: {user.role}") # to debug delete later
            if user is not None:
                login(request, user)
                # redirect to each dashbaord based on role
                if user.role == 'student':
                    print("Redirecting to student dashboard")
                    return redirect('student_dashboard')
                elif user.role == 'tutor':
                    print("Redirecting to tutor dashboard")
                    return redirect('tutor_dashboard')
                elif user.role == 'admin':
                    print("Redirecting to admin dashboard")
                    return redirect('admin_dashboard')

                # if invalid role redirect to home
                messages.error(request, "Invalid role. Please contact support.")
                return redirect('home')

        
        messages.error(request, "The credentials provided were invalid!")
        return self.render(form=form)

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
        login(self.request, self.object)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(settings.REDIRECT_URL_WHEN_LOGGED_IN)
    

# show all lesson requests  
def list_requests(request):
    requests = LessonRequest.objects.all().order_by('-created_at')
    return render(request, 'admin/request_list.html', {'requests': requests})

# remove or reject lesson request 
def handle_request(request, pk):
    # approve or reject request
    lesson_request = get_object_or_404(LessonRequest, pk=pk)

    if request.method == 'POST':
        action = request.POST.get('action')  # action to approve or reject

        if action == 'approve':
            # create lesson schedule for approved request
            LessonSchedule.objects.create(
                tutor=request.POST.get('tutor'),
                student=lesson_request.student,
                subject=lesson_request.subject,
                start_time=request.POST.get('start_time'),
                end_time=request.POST.get('end_time'),
                frequency=lesson_request.frequency,
                location=request.POST.get('location'),
                status='scheduled',
            )
            lesson_request.status = 'approved'
            messages.success(request, "Request approved and lesson scheduled!")
        elif action == 'reject':
            lesson_request.status = 'rejected'
            messages.warning(request, "Request rejected.")
        lesson_request.save()

        return redirect('list_requests')

    tutors = request.user.objects.filter(role='tutor')  # only tutors
    return render(request, 'admin/handle_request.html', {'request': lesson_request, 'tutors': tutors})

def lesson_list(request):
    # show all scheduled lesson
    lessons = LessonSchedule.objects.all().order_by('start_time')
    return render(request, 'admin/lesson_list.html', {'lessons': lessons})

class LessonScheduleForm(ModelForm):
    class Meta:
        model = LessonSchedule
        fields = ['tutor', 'student', 'subject', 'start_time', 'end_time', 'frequency', 'location']
