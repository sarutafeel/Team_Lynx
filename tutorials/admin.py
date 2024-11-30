from django.contrib import admin
from .models import LessonRequest, LessonSchedule
from .models import User
# Register your models here.

admin.site.register(LessonRequest)
admin.site.register(LessonRequest)

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'role', 'email')
    fields = ('username', 'role', 'email', 'first_name', 'last_name', 'password')

class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('role',)}),  # Include the custom role field
    )

admin.site.register(User, CustomUserAdmin)