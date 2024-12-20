"""
URL configuration for code_tutors project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from tutorials import views
from django.views.generic import TemplateView
from tutorials.views import student_dashboard, tutor_dashboard, admin_dashboard, create_invoice, FeedbackView,delete_invoice, submit_student_request,submit_tutor_request, cancel_lesson, cancel_student_request, cancel_tutor_request



urlpatterns = [
    path('admin/analytics/', views.admin_analytics, name='admin_analytics'),
    path('admin/create_invoice/', views.create_invoice, name="create_invoice"),
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'), 
    path('admin/delete-invoice/<int:invoice_id>/', views.delete_invoice, name='delete_invoice'),
    path('admin/feedback/', views.admin_feedback, name='admin_feedback'),
    path('admin/invoices/', views.admin_invoices, name='admin_invoices'),
    path('admin/lesson/<int:pk>/edit/', views.edit_lesson, name='edit_lesson'),
    path('admin/lesson/<int:pk>/delete/', views.delete_lesson, name='delete_lesson'),
    path('admin/requests/', views.admin_request_list, name='admin_request_list'),
    path('admin/pair/<int:student_request_id>/<int:tutor_request_id>/', views.pair_request, name='pair_request'),
    path('admin/', admin.site.urls),  # Built-in Django admin
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('log_in/', views.LogInView.as_view(), name='log_in'),
    path('invoices/<int:invoice_id>/', views.view_invoice, name='view_invoice'),
    path('invoices/<int:invoice_id>/mark_paid/', views.mark_paid, name='mark_paid'),
    path('log_out/', views.log_out, name='log_out'),
    path('password/', views.PasswordView.as_view(), name='password'),
    path('profile/', views.ProfileUpdateView.as_view(), name='profile'),
    path('sign_up/', views.SignUpView.as_view(), name='sign_up'),
    path("student/dashboard/", views.student_dashboard, name="student_dashboard"),
    path("student/invoices/", views.student_invoices, name="student_invoices"),
    path("student/request/", views.submit_student_request, name="submit_student_request"),
    path("student/requests/", views.student_requests, name="student_requests"),
    path('submit-feedback/', views.FeedbackView.as_view(), name='submit_feedback'),
    path('tutor/dashboard/', views.tutor_dashboard, name='tutor_dashboard'),
    path('tutor_sign_up/', views.TutorSignUpView.as_view(), name='tutor_sign_up'),
    path('tutor/requests/', views.tutor_requests, name='tutor_requests'),
    path('tutor/request/', views.submit_tutor_request, name='submit_tutor_request'),
    path('lesson/<int:lesson_id>/cancel/', cancel_lesson, name='cancel_lesson'),
    path('student/request/<int:request_id>/cancel/', cancel_student_request, name='cancel_student_request'),
    path('tutor/request/<int:request_id>/cancel/', cancel_tutor_request, name='cancel_tutor_request'),

]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
