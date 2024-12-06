from django.contrib import admin
from .models import Invoice, Student

class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('student', 'tutor', 'amount', 'status', 'due_date')
    list_filter = ('status',)
    search_fields = ('student__user__username', 'tutor__user__username')

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "student":
            kwargs["queryset"] = Student.objects.all()  # Ensure all students are included
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


admin.site.register(Invoice, InvoiceAdmin)  # Ensure this is not repeated
