from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Sum
from django.utils import timezone


class Delivery(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_IN_TRANSIT = 'in_transit'
    STATUS_PARTIALLY_RECEIVED = 'partially_received'
    STATUS_RECEIVED = 'received'
    STATUS_REJECTED = 'rejected'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_IN_TRANSIT, 'In Transit'),
        (STATUS_PARTIALLY_RECEIVED, 'Partially Received'),
        (STATUS_RECEIVED, 'Received'),
        (STATUS_REJECTED, 'Rejected'),
    ]

    po = models.ForeignKey('purchase_orders.PurchaseOrder', on_delete=models.CASCADE, related_name='deliveries')
    po_item = models.ForeignKey('purchase_orders.PurchaseOrderItem', on_delete=models.CASCADE, related_name='deliveries')
    delivery_reference_code = models.CharField(max_length=120)
    delivery_date = models.DateField(default=timezone.now)
    delivered_quantity = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal('0.00'))
    pending_quantity_after_delivery = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal('0.00'))
    delivery_location = models.CharField(max_length=255, blank=True)
    site_received_by = models.CharField(max_length=120, blank=True)
    quality_checked_by = models.CharField(max_length=120, blank=True)
    delivery_status = models.CharField(max_length=30, choices=STATUS_CHOICES, default=STATUS_PENDING)
    remarks = models.TextField(blank=True)
    quality_check_report = models.FileField(upload_to='po_documents/quality_reports/', blank=True, null=True)
    site_receiving_report = models.FileField(upload_to='po_documents/site_receiving/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['delivery_date', 'id']

    def __str__(self):
        return f'{self.po.po_number} - {self.delivery_reference_code}'

    def clean(self):
        if self.po_item_id and self.po_id and self.po_item.po_id != self.po_id:
            raise ValidationError('Selected PO item does not belong to the purchase order.')
        prior_total = self.po_item.deliveries.exclude(pk=self.pk).exclude(delivery_status=self.STATUS_REJECTED).aggregate(
            total=Sum('delivered_quantity')
        )['total'] or Decimal('0.00')
        if prior_total + (self.delivered_quantity or Decimal('0.00')) > (self.po_item.ordered_quantity or Decimal('0.00')):
            raise ValidationError('Delivery quantity cannot exceed ordered quantity for the selected PO item.')

    def save(self, *args, **kwargs):
        self.pending_quantity_after_delivery = max(
            (self.po_item.ordered_quantity or Decimal('0.00'))
            - ((self.po_item.deliveries.exclude(pk=self.pk).exclude(delivery_status=self.STATUS_REJECTED).aggregate(
                total=Sum('delivered_quantity')
            )['total'] or Decimal('0.00')) + (self.delivered_quantity or Decimal('0.00'))),
            Decimal('0.00')
        )
        self.full_clean()
        super().save(*args, **kwargs)
        self.po_item.update_delivery_totals()
        self.po.refresh_progress()


class DeliveryInvoiceChallan(models.Model):
    VERIFY_PENDING = 'pending'
    VERIFY_VERIFIED = 'verified'
    VERIFY_REJECTED = 'rejected'
    VERIFICATION_STATUS_CHOICES = [
        (VERIFY_PENDING, 'Pending'),
        (VERIFY_VERIFIED, 'Verified'),
        (VERIFY_REJECTED, 'Rejected'),
    ]

    po = models.ForeignKey('purchase_orders.PurchaseOrder', on_delete=models.CASCADE, related_name='invoice_challans')
    delivery = models.ForeignKey(Delivery, on_delete=models.CASCADE, related_name='invoice_challans')
    challan_number = models.CharField(max_length=120, blank=True)
    challan_date = models.DateField(null=True, blank=True)
    invoice_number = models.CharField(max_length=120, blank=True)
    invoice_date = models.DateField(null=True, blank=True)
    invoice_amount = models.DecimalField(max_digits=16, decimal_places=2, default=Decimal('0.00'))
    gst_amount = models.DecimalField(max_digits=16, decimal_places=2, default=Decimal('0.00'))
    uploaded_challan = models.FileField(upload_to='po_documents/challans/', blank=True, null=True)
    uploaded_invoice = models.FileField(upload_to='po_documents/invoices/', blank=True, null=True)
    verification_status = models.CharField(
        max_length=20,
        choices=VERIFICATION_STATUS_CHOICES,
        default=VERIFY_PENDING,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-invoice_date', '-challan_date', '-id']

    def __str__(self):
        return self.invoice_number or self.challan_number or f'{self.po.po_number} Invoice'
