from django.contrib import admin

from .models import StaffProfile


@admin.register(StaffProfile)
class StaffProfileAdmin(admin.ModelAdmin):
    list_display = ('staff_name', 'employee_id', 'department', 'designation', 'role', 'is_active')
    list_filter = ('role', 'department', 'is_active')
    search_fields = ('staff_name', 'employee_id', 'email', 'user__username')

