from django.contrib import admin

from .models import Delivery, DeliveryInvoiceChallan


@admin.register(Delivery)
class DeliveryAdmin(admin.ModelAdmin):
    list_display = ('delivery_reference_code', 'po', 'po_item', 'delivery_date', 'delivered_quantity', 'delivery_status')
    list_filter = ('delivery_status', 'delivery_date')
    search_fields = ('delivery_reference_code', 'po__po_number', 'po_item__material_name')


@admin.register(DeliveryInvoiceChallan)
class DeliveryInvoiceChallanAdmin(admin.ModelAdmin):
    list_display = ('po', 'invoice_number', 'challan_number', 'invoice_amount', 'verification_status')
    list_filter = ('verification_status',)
    search_fields = ('po__po_number', 'invoice_number', 'challan_number')
