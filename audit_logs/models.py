from django.conf import settings
from django.db import models
from django.utils import timezone


class VendorActivityLog(models.Model):
    TYPE_ASSIGNED = 'assigned'
    TYPE_REASSIGNED = 'reassigned'
    TYPE_TASK_CREATED = 'task_created'
    TYPE_TASK_UPDATED = 'task_updated'
    TYPE_DOCUMENT_UPLOADED = 'document_uploaded'
    TYPE_PO_CREATED = 'po_created'
    TYPE_DELIVERY_UPDATED = 'delivery_updated'
    TYPE_PAYMENT_FOLLOWUP = 'payment_followup'
    TYPE_NOTE_ADDED = 'note_added'
    TYPE_CHOICES = [
        (TYPE_ASSIGNED, 'Assigned to Staff'),
        (TYPE_REASSIGNED, 'Reassigned'),
        (TYPE_TASK_CREATED, 'Task Created'),
        (TYPE_TASK_UPDATED, 'Task Updated'),
        (TYPE_DOCUMENT_UPLOADED, 'Document Uploaded'),
        (TYPE_PO_CREATED, 'PO Created'),
        (TYPE_DELIVERY_UPDATED, 'Delivery Updated'),
        (TYPE_PAYMENT_FOLLOWUP, 'Payment Follow-up'),
        (TYPE_NOTE_ADDED, 'Note Added'),
    ]

    vendor = models.ForeignKey('core.Vendor', on_delete=models.CASCADE, related_name='activity_logs')
    activity_type = models.CharField(max_length=30, choices=TYPE_CHOICES)
    performed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='vendor_activity_entries',
    )
    description = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'vendor_activity_logs'
        ordering = ['-created_at', '-id']

    def __str__(self):
        return f'{self.vendor} - {self.activity_type}'

