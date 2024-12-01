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
from tutorials.views import student_dashboard, tutor_dashboard, admin_dashboard


urlpatterns = [
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),  # Custom admin dashboard
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
<<<<<<< HEAD
    path('tutor_sign_up/', views.TutorSignUpView.as_view(), name='tutor_sign_up'),
=======
    path('student/dashboard/', views.student_dashboard, name='student_dashboard'),
    path('tutor/dashboard/', views.tutor_dashboard, name='tutor_dashboard'),
>>>>>>> origin/Adel
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
