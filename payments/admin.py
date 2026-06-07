from django.contrib import admin

from .models import VendorPayment


@admin.register(VendorPayment)
class VendorPaymentAdmin(admin.ModelAdmin):
    list_display = ('payment_reference_code', 'po', 'vendor', 'payment_stage', 'net_payable', 'payment_status')
    list_filter = ('payment_stage', 'payment_status', 'payment_mode')
    search_fields = ('payment_reference_code', 'po__po_number', 'vendor__company_name', 'bank_transaction_id')
