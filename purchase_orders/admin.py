from django.contrib import admin

from .models import PurchaseOrder, PurchaseOrderActivityLog, PurchaseOrderItem, PurchaseOrderReferenceCode


class PurchaseOrderItemInline(admin.TabularInline):
    model = PurchaseOrderItem
    extra = 0


class PurchaseOrderReferenceCodeInline(admin.TabularInline):
    model = PurchaseOrderReferenceCode
    extra = 0


@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = (
        'po_number',
        'po_date',
        'vendor',
        'vendor_tracking_id',
        'vendor_tracking_name',
        'project_site_name',
        'dispatch_origin',
        'total_po_value',
        'paid_amount',
        'outstanding_amount',
        'status',
    )
    list_filter = ('status', 'business_division', 'department')
    search_fields = (
        'po_number',
        'vendor_tracking_id',
        'vendor_tracking_name',
        'project_site_name',
        'delivery_address',
        'dispatch_origin',
        'vendor__company_name',
    )
    inlines = [PurchaseOrderItemInline, PurchaseOrderReferenceCodeInline]


@admin.register(PurchaseOrderActivityLog)
class PurchaseOrderActivityLogAdmin(admin.ModelAdmin):
    list_display = ('po', 'action', 'actor', 'created_at')
    search_fields = ('po__po_number', 'action', 'description')
