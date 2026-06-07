from django.contrib import admin

from .models import VendorActivityLog


@admin.register(VendorActivityLog)
class VendorActivityLogAdmin(admin.ModelAdmin):
    list_display = ('vendor', 'activity_type', 'performed_by', 'created_at')
    list_filter = ('activity_type',)
    search_fields = ('vendor__company_name', 'vendor__vendor_id', 'description')

