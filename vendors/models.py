from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.utils import timezone


class VendorAssignment(models.Model):
    ROLE_PRIMARY = 'primary'
    ROLE_SUPPORTING = 'supporting'
    ASSIGNMENT_ROLE_CHOICES = [
        (ROLE_PRIMARY, 'Primary Staff'),
        (ROLE_SUPPORTING, 'Supporting Staff'),
    ]

    STATUS_ACTIVE = 'active'
    STATUS_REASSIGNED = 'reassigned'
    STATUS_REMOVED = 'removed'
    STATUS_ON_HOLD = 'on_hold'
    STATUS_CHOICES = [
        (STATUS_ACTIVE, 'Active'),
        (STATUS_REASSIGNED, 'Reassigned'),
        (STATUS_REMOVED, 'Removed'),
        (STATUS_ON_HOLD, 'On Hold'),
    ]

    vendor = models.ForeignKey('core.Vendor', on_delete=models.CASCADE, related_name='assignments')
    assigned_staff = models.ForeignKey('accounts.StaffProfile', on_delete=models.PROTECT, related_name='vendor_assignments')
    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='assigned_vendor_records',
    )
    assignment_role = models.CharField(max_length=20, choices=ASSIGNMENT_ROLE_CHOICES, default=ROLE_PRIMARY)
    assignment_date = models.DateTimeField(default=timezone.now)
    start_date = models.DateField(default=timezone.localdate)
    end_date = models.DateField(null=True, blank=True)
    assignment_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_ACTIVE)
    assignment_reason = models.CharField(max_length=255, blank=True)
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'vendor_assignments'
        ordering = ['vendor__company_name', 'assignment_role', '-start_date']
        constraints = [
            models.UniqueConstraint(
                fields=['vendor'],
                condition=Q(assignment_role='primary', assignment_status='active'),
                name='unique_active_primary_vendor_assignment',
            ),
        ]

    def __str__(self):
        return f'{self.vendor} -> {self.assigned_staff}'

    def clean(self):
        if self.end_date and self.start_date and self.end_date < self.start_date:
            raise ValidationError('End date cannot be earlier than start date.')
        if self.assignment_role == self.ROLE_PRIMARY and self.assignment_status == self.STATUS_ACTIVE:
            duplicate = VendorAssignment.objects.filter(
                vendor=self.vendor,
                assignment_role=self.ROLE_PRIMARY,
                assignment_status=self.STATUS_ACTIVE,
            ).exclude(pk=self.pk)
            if duplicate.exists():
                raise ValidationError('This vendor already has an active primary staff assignment.')

    @property
    def is_current(self):
        return self.assignment_status == self.STATUS_ACTIVE and (not self.end_date or self.end_date >= timezone.localdate())


class VendorAssignmentHistory(models.Model):
    vendor = models.ForeignKey('core.Vendor', on_delete=models.CASCADE, related_name='assignment_history')
    previous_staff = models.ForeignKey(
        'accounts.StaffProfile',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='previous_vendor_histories',
    )
    new_staff = models.ForeignKey(
        'accounts.StaffProfile',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='new_vendor_histories',
    )
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='vendor_assignment_changes',
    )
    changed_date = models.DateTimeField(default=timezone.now)
    reason = models.CharField(max_length=255, blank=True)
    remarks = models.TextField(blank=True)

    class Meta:
        db_table = 'vendor_assignment_history'
        ordering = ['-changed_date', '-id']

    def __str__(self):
        return f'{self.vendor} reassigned on {self.changed_date:%Y-%m-%d %H:%M}'
