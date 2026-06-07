from django.contrib import admin

from core.models import Vendor

from .models import VendorAssignment, VendorAssignmentHistory


@admin.register(Vendor)
class VendorMasterAdmin(admin.ModelAdmin):
    list_display = (
        'vendor_id',
        'vendor_name',
        'company_name',
        'contact_person',
        'mobile_number',
        'status',
        'qualification_status',
    )
    list_filter = ('status', 'qualification_status', 'vendor_category', 'vendor_type')
    search_fields = ('vendor_id', 'vendor_name', 'company_name', 'gst_no', 'pan_no', 'contact_person')
    readonly_fields = ('vendor_id', 'created_at')


@admin.register(VendorAssignment)
class VendorAssignmentAdmin(admin.ModelAdmin):
    list_display = ('vendor', 'assigned_staff', 'assignment_role', 'assignment_status', 'start_date', 'end_date')
    list_filter = ('assignment_role', 'assignment_status')
    search_fields = ('vendor__company_name', 'vendor__vendor_id', 'assigned_staff__staff_name')


@admin.register(VendorAssignmentHistory)
class VendorAssignmentHistoryAdmin(admin.ModelAdmin):
    list_display = ('vendor', 'previous_staff', 'new_staff', 'changed_by', 'changed_date')
    search_fields = ('vendor__company_name', 'vendor__vendor_id', 'reason')
