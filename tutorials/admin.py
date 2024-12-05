from django.contrib import admin
from .models import Feedback, LessonSchedule

# Register your models here.
@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'message', 'posted', 'lesson')  # Fields to display in the admin panel
    search_fields =('name', 'email')
    list_filter = ('posted',)

@admin.register(LessonSchedule)
class LessonScheduleAdmin(admin.ModelAdmin):
    list_display = ('tutor', 'student', 'subject', 'start_time', 'end_time', 'status')
    search_fields = ('subject', 'student__first_name', 'student__last_name', 'tutor__user__username')