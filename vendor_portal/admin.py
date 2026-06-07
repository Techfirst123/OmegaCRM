from django.contrib import admin

from .models import (
    VendorDailyUpdate,
    VendorDocument,
    VendorIssue,
    VendorMedia,
    VendorNotification,
    VendorPortalSession,
    VendorProjectAssignment,
    VendorReview,
    VendorUser,
)


@admin.register(VendorUser)
class VendorUserAdmin(admin.ModelAdmin):
    list_display = ('user', 'vendor', 'role', 'mobile_number', 'is_active')
    list_filter = ('role', 'is_active')
    search_fields = ('user__username', 'vendor__company_name', 'mobile_number', 'email')


@admin.register(VendorProjectAssignment)
class VendorProjectAssignmentAdmin(admin.ModelAdmin):
    list_display = ('project', 'vendor_user', 'site_name', 'work_type', 'capacity_mw', 'is_active')
    list_filter = ('is_active', 'district', 'state', 'country')
    search_fields = ('project__project_name', 'site_name', 'site_code', 'vendor_user__user__username')


@admin.register(VendorDailyUpdate)
class VendorDailyUpdateAdmin(admin.ModelAdmin):
    list_display = ('assignment', 'update_date', 'work_category', 'quantity_completed', 'progress_percentage', 'status')
    list_filter = ('status', 'update_date')
    search_fields = ('assignment__project__project_name', 'work_category', 'work_description')


admin.site.register(VendorMedia)
admin.site.register(VendorDocument)
admin.site.register(VendorIssue)
admin.site.register(VendorReview)
admin.site.register(VendorNotification)
admin.site.register(VendorPortalSession)
