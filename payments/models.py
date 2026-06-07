from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Sum


class VendorPayment(models.Model):
    STAGE_ADVANCE = 'advance'
    STAGE_DISPATCH = 'against_dispatch'
    STAGE_DELIVERY = 'against_delivery'
    STAGE_INSTALLATION = 'after_installation'
    STAGE_RETENTION = 'retention'
    STAGE_FINAL = 'final_payment'
    PAYMENT_STAGE_CHOICES = [
        (STAGE_ADVANCE, 'Advance'),
        (STAGE_DISPATCH, 'Against Dispatch'),
        (STAGE_DELIVERY, 'Against Delivery'),
        (STAGE_INSTALLATION, 'After Installation'),
        (STAGE_RETENTION, 'Retention'),
        (STAGE_FINAL, 'Final Payment'),
    ]

    MODE_NEFT = 'neft'
    MODE_RTGS = 'rtgs'
    MODE_UPI = 'upi'
    MODE_CHEQUE = 'cheque'
    MODE_CASH = 'cash'
    PAYMENT_MODE_CHOICES = [
        (MODE_NEFT, 'NEFT'),
        (MODE_RTGS, 'RTGS'),
        (MODE_UPI, 'UPI'),
        (MODE_CHEQUE, 'Cheque'),
        (MODE_CASH, 'Cash'),
    ]

    STATUS_PENDING = 'pending'
    STATUS_APPROVED = 'approved'
    STATUS_PAID = 'paid'
    STATUS_HOLD = 'hold'
    STATUS_REJECTED = 'rejected'
    PAYMENT_STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_APPROVED, 'Approved'),
        (STATUS_PAID, 'Paid'),
        (STATUS_HOLD, 'Hold'),
        (STATUS_REJECTED, 'Rejected'),
    ]

    po = models.ForeignKey('purchase_orders.PurchaseOrder', on_delete=models.CASCADE, related_name='payments')
    vendor = models.ForeignKey('core.Vendor', on_delete=models.PROTECT, related_name='vendor_payments')
    payment_reference_code = models.CharField(max_length=120)
    related_delivery = models.ForeignKey(
        'deliveries.Delivery',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='payments',
    )
    related_invoice = models.ForeignKey(
        'deliveries.DeliveryInvoiceChallan',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='payments',
    )
    payment_stage = models.CharField(max_length=30, choices=PAYMENT_STAGE_CHOICES)
    payment_percentage = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal('0.00'))
    payment_amount = models.DecimalField(max_digits=16, decimal_places=2, default=Decimal('0.00'))
    tds_deduction = models.DecimalField(max_digits=16, decimal_places=2, default=Decimal('0.00'))
    gst_amount = models.DecimalField(max_digits=16, decimal_places=2, default=Decimal('0.00'))
    net_payable = models.DecimalField(max_digits=16, decimal_places=2, default=Decimal('0.00'))
    payment_due_date = models.DateField(null=True, blank=True)
    payment_paid_date = models.DateField(null=True, blank=True)
    payment_mode = models.CharField(max_length=20, choices=PAYMENT_MODE_CHOICES, blank=True)
    bank_transaction_id = models.CharField(max_length=120, blank=True)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default=STATUS_PENDING)
    uploaded_payment_proof = models.FileField(upload_to='po_documents/payment_proofs/', blank=True, null=True)
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['payment_due_date', 'id']
        unique_together = ('po', 'payment_reference_code')

    def __str__(self):
        return f'{self.po.po_number} - {self.payment_reference_code}'

    def clean(self):
        if self.vendor_id and self.po_id and self.po.vendor_id != self.vendor_id:
            raise ValidationError('Selected vendor must match the purchase order vendor.')
        previous_total = self.po.payments.exclude(pk=self.pk).exclude(payment_status=self.STATUS_REJECTED).aggregate(
            total=Sum('net_payable')
        )['total'] or Decimal('0.00')
        projected = previous_total + ((self.payment_amount or Decimal('0.00')) + (self.gst_amount or Decimal('0.00')) - (self.tds_deduction or Decimal('0.00')))
        if self.po.total_po_value and projected > self.po.total_po_value:
            raise ValidationError('Payment amount cannot exceed the total PO value.')

    def save(self, *args, **kwargs):
        self.net_payable = (self.payment_amount or Decimal('0.00')) + (self.gst_amount or Decimal('0.00')) - (self.tds_deduction or Decimal('0.00'))
        self.full_clean()
        super().save(*args, **kwargs)
        self.po.refresh_progress()
