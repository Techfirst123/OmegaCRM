from django.conf import settings
from django.db import models
from django.utils import timezone


class VendorTask(models.Model):
    TYPE_DOCUMENT_COLLECTION = 'document_collection'
    TYPE_QUOTATION = 'quotation_followup'
    TYPE_PO = 'po_followup'
    TYPE_DELIVERY = 'delivery_followup'
    TYPE_PAYMENT = 'payment_followup'
    TYPE_QUALITY = 'quality_issue'
    TYPE_COMPLIANCE = 'compliance'
    TYPE_GENERAL = 'general'
    TASK_TYPE_CHOICES = [
        (TYPE_DOCUMENT_COLLECTION, 'Document Collection'),
        (TYPE_QUOTATION, 'Quotation Follow-up'),
        (TYPE_PO, 'PO Follow-up'),
        (TYPE_DELIVERY, 'Delivery Follow-up'),
        (TYPE_PAYMENT, 'Payment Follow-up'),
        (TYPE_QUALITY, 'Quality Issue'),
        (TYPE_COMPLIANCE, 'Compliance'),
        (TYPE_GENERAL, 'General'),
    ]

    PRIORITY_LOW = 'low'
    PRIORITY_MEDIUM = 'medium'
    PRIORITY_HIGH = 'high'
    PRIORITY_URGENT = 'urgent'
    PRIORITY_CHOICES = [
        (PRIORITY_LOW, 'Low'),
        (PRIORITY_MEDIUM, 'Medium'),
        (PRIORITY_HIGH, 'High'),
        (PRIORITY_URGENT, 'Urgent'),
    ]

    STATUS_PENDING = 'pending'
    STATUS_IN_PROGRESS = 'in_progress'
    STATUS_COMPLETED = 'completed'
    STATUS_OVERDUE = 'overdue'
    STATUS_CANCELLED = 'cancelled'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_IN_PROGRESS, 'In Progress'),
        (STATUS_COMPLETED, 'Completed'),
        (STATUS_OVERDUE, 'Overdue'),
        (STATUS_CANCELLED, 'Cancelled'),
    ]

    vendor = models.ForeignKey('core.Vendor', on_delete=models.CASCADE, related_name='vendor_tasks')
    assigned_staff = models.ForeignKey('accounts.StaffProfile', on_delete=models.PROTECT, related_name='assigned_tasks')
    task_title = models.CharField(max_length=255)
    task_type = models.CharField(max_length=40, choices=TASK_TYPE_CHOICES, default=TYPE_GENERAL)
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default=PRIORITY_MEDIUM)
    due_date = models.DateField()
    task_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='created_vendor_tasks',
    )
    completed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='completed_vendor_tasks',
    )
    completion_date = models.DateTimeField(null=True, blank=True)
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'vendor_tasks'
        ordering = ['due_date', '-priority', '-created_at']

    def __str__(self):
        return f'{self.vendor} - {self.task_title}'

    def refresh_status(self, save=True):
        if self.task_status == self.STATUS_COMPLETED:
            if not self.completion_date:
                self.completion_date = timezone.now()
        elif self.task_status != self.STATUS_CANCELLED and self.due_date and self.due_date < timezone.localdate():
            self.task_status = self.STATUS_OVERDUE
        elif self.task_status == self.STATUS_OVERDUE and self.due_date >= timezone.localdate():
            self.task_status = self.STATUS_PENDING
        if save:
            self.save()

    @property
    def is_open(self):
        return self.task_status in {self.STATUS_PENDING, self.STATUS_IN_PROGRESS, self.STATUS_OVERDUE}

