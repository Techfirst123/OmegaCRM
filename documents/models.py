from django.conf import settings
from django.db import models


class BusinessDocument(models.Model):
    DOC_PO_COPY = 'po_copy'
    DOC_VENDOR_QUOTATION = 'vendor_quotation'
    DOC_INVOICE = 'invoice'
    DOC_CHALLAN = 'challan'
    DOC_EWAY_BILL = 'eway_bill'
    DOC_LR_COPY = 'lr_copy'
    DOC_PAYMENT_PROOF = 'payment_proof'
    DOC_QUALITY_CHECK = 'quality_check'
    DOC_SITE_RECEIVING = 'site_receiving'
    DOC_OTHER = 'other'
    DOCUMENT_TYPE_CHOICES = [
        (DOC_PO_COPY, 'PO Copy'),
        (DOC_VENDOR_QUOTATION, 'Vendor Quotation'),
        (DOC_INVOICE, 'Invoice'),
        (DOC_CHALLAN, 'Challan'),
        (DOC_EWAY_BILL, 'E-way Bill'),
        (DOC_LR_COPY, 'LR Copy'),
        (DOC_PAYMENT_PROOF, 'Payment Proof'),
        (DOC_QUALITY_CHECK, 'Quality Check Report'),
        (DOC_SITE_RECEIVING, 'Site Receiving Report'),
        (DOC_OTHER, 'Other'),
    ]

    po = models.ForeignKey(
        'purchase_orders.PurchaseOrder',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='documents',
    )
    delivery = models.ForeignKey(
        'deliveries.Delivery',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='documents',
    )
    vehicle = models.ForeignKey(
        'transport.VehicleMovement',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='documents',
    )
    payment = models.ForeignKey(
        'payments.VendorPayment',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='documents',
    )
    reference_code = models.ForeignKey(
        'purchase_orders.PurchaseOrderReferenceCode',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='documents',
    )
    document_type = models.CharField(max_length=30, choices=DOCUMENT_TYPE_CHOICES, default=DOC_OTHER)
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='po_documents/library/')
    notes = models.TextField(blank=True)
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='uploaded_business_documents',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at', '-id']

    def __str__(self):
        return self.title


class NotificationLog(models.Model):
    CHANNEL_EMAIL = 'email'
    CHANNEL_WHATSAPP = 'whatsapp'
    CHANNEL_CHOICES = [
        (CHANNEL_EMAIL, 'Email'),
        (CHANNEL_WHATSAPP, 'WhatsApp'),
    ]

    STATUS_PENDING = 'pending'
    STATUS_SENT = 'sent'
    STATUS_FAILED = 'failed'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_SENT, 'Sent'),
        (STATUS_FAILED, 'Failed'),
    ]

    EVENT_DELIVERY_DELAYED = 'delivery_delayed'
    EVENT_VEHICLE_REACHED = 'vehicle_reached'
    EVENT_PAYMENT_DUE = 'payment_due'
    EVENT_INVOICE_PENDING = 'invoice_pending'
    EVENT_PO_PARTIAL = 'po_partial'
    EVENT_PO_FULL = 'po_full'
    EVENT_APPROVAL_REQUIRED = 'approval_required'
    EVENT_CHOICES = [
        (EVENT_DELIVERY_DELAYED, 'Delivery Delayed'),
        (EVENT_VEHICLE_REACHED, 'Vehicle Reached Site'),
        (EVENT_PAYMENT_DUE, 'Pending Payment Due'),
        (EVENT_INVOICE_PENDING, 'Invoice Pending Verification'),
        (EVENT_PO_PARTIAL, 'PO Partially Delivered'),
        (EVENT_PO_FULL, 'PO Fully Delivered'),
        (EVENT_APPROVAL_REQUIRED, 'Payment Approval Required'),
    ]

    po = models.ForeignKey('purchase_orders.PurchaseOrder', on_delete=models.CASCADE, null=True, blank=True, related_name='notifications')
    delivery = models.ForeignKey('deliveries.Delivery', on_delete=models.CASCADE, null=True, blank=True, related_name='notifications')
    payment = models.ForeignKey('payments.VendorPayment', on_delete=models.CASCADE, null=True, blank=True, related_name='notifications')
    event_type = models.CharField(max_length=40, choices=EVENT_CHOICES)
    channel = models.CharField(max_length=20, choices=CHANNEL_CHOICES, default=CHANNEL_EMAIL)
    recipient_name = models.CharField(max_length=120, blank=True)
    recipient_contact = models.CharField(max_length=255)
    subject = models.CharField(max_length=255, blank=True)
    message = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at', '-id']

    def __str__(self):
        return f'{self.event_type} - {self.recipient_contact}'
