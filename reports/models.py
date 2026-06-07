from django.conf import settings
from django.db import models


class SavedReport(models.Model):
    REPORT_PO_SUMMARY = 'po_summary'
    REPORT_VENDOR_PO = 'vendor_po'
    REPORT_MATERIAL_DELIVERY = 'material_delivery'
    REPORT_VEHICLE_TRACKING = 'vehicle_tracking'
    REPORT_PENDING_DELIVERY = 'pending_delivery'
    REPORT_PART_PAYMENT = 'part_payment'
    REPORT_OUTSTANDING_PAYMENT = 'outstanding_payment'
    REPORT_INVOICE_PAYMENT = 'invoice_payment'
    REPORT_TYPE_CHOICES = [
        (REPORT_PO_SUMMARY, 'PO Summary Report'),
        (REPORT_VENDOR_PO, 'Vendor-wise PO Report'),
        (REPORT_MATERIAL_DELIVERY, 'Material-wise Delivery Report'),
        (REPORT_VEHICLE_TRACKING, 'Vehicle Tracking Report'),
        (REPORT_PENDING_DELIVERY, 'Pending Delivery Report'),
        (REPORT_PART_PAYMENT, 'Part-wise Payment Report'),
        (REPORT_OUTSTANDING_PAYMENT, 'Outstanding Vendor Payment Report'),
        (REPORT_INVOICE_PAYMENT, 'Invoice vs Payment Report'),
    ]

    name = models.CharField(max_length=150)
    report_type = models.CharField(max_length=40, choices=REPORT_TYPE_CHOICES)
    filters_json = models.TextField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='saved_reports',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name
