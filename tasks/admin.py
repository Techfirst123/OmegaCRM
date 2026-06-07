from django.contrib import admin

from .models import VendorTask


@admin.register(VendorTask)
class VendorTaskAdmin(admin.ModelAdmin):
    list_display = ('task_title', 'vendor', 'assigned_staff', 'priority', 'due_date', 'task_status')
    list_filter = ('task_type', 'priority', 'task_status')
    search_fields = ('task_title', 'vendor__company_name', 'vendor__vendor_id', 'assigned_staff__staff_name')

