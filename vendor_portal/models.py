from decimal import Decimal

from django.conf import settings
from django.db import models
from django.db.models import Max, Sum
from django.utils import timezone


class VendorUser(models.Model):
    ROLE_VENDOR_ADMIN = 'vendor_admin'
    ROLE_VENDOR_SUPERVISOR = 'vendor_supervisor'
    ROLE_VENDOR_ENGINEER = 'vendor_engineer'
    ROLE_VENDOR_OPERATOR = 'vendor_operator'
    ROLE_CHOICES = [
        (ROLE_VENDOR_ADMIN, 'Vendor Admin'),
        (ROLE_VENDOR_SUPERVISOR, 'Vendor Supervisor'),
        (ROLE_VENDOR_ENGINEER, 'Vendor Engineer'),
        (ROLE_VENDOR_OPERATOR, 'Vendor Operator'),
    ]

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='vendor_profile')
    vendor = models.ForeignKey('core.Vendor', on_delete=models.CASCADE, related_name='portal_users')
    role = models.CharField(max_length=40, choices=ROLE_CHOICES, default=ROLE_VENDOR_OPERATOR)
    mobile_number = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True)
    is_active = models.BooleanField(default=True)
    otp_code = models.CharField(max_length=12, blank=True)
    otp_generated_at = models.DateTimeField(null=True, blank=True)
    otp_verified_at = models.DateTimeField(null=True, blank=True)
    last_login_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'vendor_portal_users'
        ordering = ['vendor__company_name', 'user__username']

    def __str__(self):
        return f'{self.vendor.company_name} - {self.user.username}'


class VendorProjectAssignment(models.Model):
    vendor_user = models.ForeignKey(VendorUser, on_delete=models.CASCADE, related_name='project_assignments')
    vendor = models.ForeignKey('core.Vendor', on_delete=models.CASCADE, related_name='portal_project_assignments')
    project = models.ForeignKey('core.ProjectMaster', on_delete=models.CASCADE, related_name='vendor_portal_assignments')
    allocation = models.ForeignKey('core.ProjectWorkAllocation', on_delete=models.SET_NULL, null=True, blank=True, related_name='portal_assignments')
    site_name = models.CharField(max_length=255, blank=True)
    site_code = models.CharField(max_length=100, blank=True)
    client_name = models.CharField(max_length=255, blank=True)
    location = models.CharField(max_length=255, blank=True)
    district = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    capacity_mw = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    work_type = models.CharField(max_length=150, blank=True)
    start_date = models.DateField(null=True, blank=True)
    completion_date = models.DateField(null=True, blank=True)
    assigned_scope = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    ai_health_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'vendor_portal_project_assignments'
        ordering = ['project__project_name', 'site_name', 'work_type']
        unique_together = ('vendor_user', 'project', 'allocation')

    def __str__(self):
        return f'{self.project.project_name} - {self.vendor_user.user.username}'

    @property
    def total_progress_percentage(self):
        if not self.capacity_mw or self.capacity_mw <= 0:
            return Decimal('0')
        completed_mw = self.approved_completed_mw
        return min((completed_mw / self.capacity_mw) * Decimal('100'), Decimal('100'))

    @property
    def approved_completed_mw(self):
        totals = self.daily_updates.filter(
            status__in=[VendorDailyUpdate.STATUS_APPROVED, VendorDailyUpdate.STATUS_VERIFIED],
            unit__iexact='mw',
        ).aggregate(total=Sum('quantity_completed'))
        quantity_total = totals['total'] or Decimal('0')
        if quantity_total > 0:
            return quantity_total
        percentage_value = self.daily_updates.filter(
            status__in=[VendorDailyUpdate.STATUS_APPROVED, VendorDailyUpdate.STATUS_VERIFIED],
        ).aggregate(max_percent=Max('progress_percentage'))['max_percent'] or Decimal('0')
        if not self.capacity_mw:
            return Decimal('0')
        return (self.capacity_mw * percentage_value) / Decimal('100')


class VendorDailyUpdate(models.Model):
    STATUS_DRAFT = 'draft'
    STATUS_SUBMITTED = 'submitted'
    STATUS_UNDER_REVIEW = 'under_review'
    STATUS_APPROVED = 'approved'
    STATUS_REJECTED = 'rejected'
    STATUS_VERIFIED = 'verified'
    STATUS_CHOICES = [
        (STATUS_DRAFT, 'Draft'),
        (STATUS_SUBMITTED, 'Submitted'),
        (STATUS_UNDER_REVIEW, 'Under Review'),
        (STATUS_APPROVED, 'Approved'),
        (STATUS_REJECTED, 'Rejected'),
        (STATUS_VERIFIED, 'Verified'),
    ]

    assignment = models.ForeignKey(VendorProjectAssignment, on_delete=models.CASCADE, related_name='daily_updates')
    vendor_user = models.ForeignKey(VendorUser, on_delete=models.CASCADE, related_name='daily_updates')
    update_date = models.DateField(default=timezone.localdate)
    work_category = models.CharField(max_length=150)
    work_description = models.TextField()
    todays_achievement = models.TextField(blank=True)
    quantity_completed = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    unit = models.CharField(max_length=50, blank=True)
    progress_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    manpower_used = models.PositiveIntegerField(default=0)
    equipment_used = models.TextField(blank=True)
    material_consumed = models.TextField(blank=True)
    issues_faced = models.TextField(blank=True)
    delay_reasons = models.TextField(blank=True)
    tomorrow_plan = models.TextField(blank=True)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default=STATUS_DRAFT)
    ai_completion_estimate = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    ai_delay_risk_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'vendor_portal_daily_updates'
        ordering = ['-update_date', '-created_at']

    def __str__(self):
        return f'{self.assignment.project.project_name} - {self.update_date}'


class VendorMedia(models.Model):
    TYPE_IMAGE = 'image'
    TYPE_VIDEO = 'video'
    MEDIA_TYPE_CHOICES = [
        (TYPE_IMAGE, 'Image'),
        (TYPE_VIDEO, 'Video'),
    ]

    assignment = models.ForeignKey(VendorProjectAssignment, on_delete=models.CASCADE, related_name='media_entries')
    daily_update = models.ForeignKey(VendorDailyUpdate, on_delete=models.CASCADE, related_name='media_entries', null=True, blank=True)
    uploaded_by = models.ForeignKey(VendorUser, on_delete=models.CASCADE, related_name='media_entries')
    media_type = models.CharField(max_length=20, choices=MEDIA_TYPE_CHOICES)
    file = models.FileField(upload_to='vendor_portal/media/')
    caption = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    gps_latitude = models.CharField(max_length=50, blank=True)
    gps_longitude = models.CharField(max_length=50, blank=True)
    captured_at = models.DateTimeField(null=True, blank=True)
    watermark_text = models.CharField(max_length=255, blank=True)
    ai_progress_detection_json = models.TextField(blank=True)
    upload_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'vendor_portal_media'
        ordering = ['-upload_date']


class VendorDocument(models.Model):
    TYPE_SITE_REPORT = 'site_report'
    TYPE_TEST_CERTIFICATE = 'test_certificate'
    TYPE_INSPECTION_REPORT = 'inspection_report'
    TYPE_DRAWING = 'drawing'
    TYPE_GENERAL = 'general'
    DOCUMENT_TYPE_CHOICES = [
        (TYPE_SITE_REPORT, 'Site Report'),
        (TYPE_TEST_CERTIFICATE, 'Test Certificate'),
        (TYPE_INSPECTION_REPORT, 'Inspection Report'),
        (TYPE_DRAWING, 'CAD Drawing'),
        (TYPE_GENERAL, 'General Document'),
    ]

    assignment = models.ForeignKey(VendorProjectAssignment, on_delete=models.CASCADE, related_name='documents')
    daily_update = models.ForeignKey(VendorDailyUpdate, on_delete=models.CASCADE, related_name='documents', null=True, blank=True)
    uploaded_by = models.ForeignKey(VendorUser, on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(max_length=40, choices=DOCUMENT_TYPE_CHOICES, default=TYPE_GENERAL)
    file = models.FileField(upload_to='vendor_portal/documents/')
    remarks = models.TextField(blank=True)
    upload_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'vendor_portal_documents'
        ordering = ['-upload_date']


class VendorIssue(models.Model):
    TYPE_MATERIAL_SHORTAGE = 'material_shortage'
    TYPE_LABOUR_SHORTAGE = 'labour_shortage'
    TYPE_TECHNICAL = 'technical_issue'
    TYPE_WEATHER = 'weather_delay'
    TYPE_SAFETY = 'safety_issue'
    TYPE_CLIENT = 'client_issue'
    TYPE_EQUIPMENT = 'equipment_breakdown'
    ISSUE_TYPE_CHOICES = [
        (TYPE_MATERIAL_SHORTAGE, 'Material Shortage'),
        (TYPE_LABOUR_SHORTAGE, 'Labour Shortage'),
        (TYPE_TECHNICAL, 'Technical Issue'),
        (TYPE_WEATHER, 'Weather Delay'),
        (TYPE_SAFETY, 'Safety Issue'),
        (TYPE_CLIENT, 'Client Issue'),
        (TYPE_EQUIPMENT, 'Equipment Breakdown'),
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
    STATUS_OPEN = 'open'
    STATUS_IN_PROGRESS = 'in_progress'
    STATUS_RESOLVED = 'resolved'
    STATUS_CLOSED = 'closed'
    STATUS_CHOICES = [
        (STATUS_OPEN, 'Open'),
        (STATUS_IN_PROGRESS, 'In Progress'),
        (STATUS_RESOLVED, 'Resolved'),
        (STATUS_CLOSED, 'Closed'),
    ]

    assignment = models.ForeignKey(VendorProjectAssignment, on_delete=models.CASCADE, related_name='issues')
    vendor_user = models.ForeignKey(VendorUser, on_delete=models.CASCADE, related_name='issues')
    issue_type = models.CharField(max_length=40, choices=ISSUE_TYPE_CHOICES)
    title = models.CharField(max_length=255)
    description = models.TextField()
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default=PRIORITY_MEDIUM)
    evidence_file = models.FileField(upload_to='vendor_portal/issues/', blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_OPEN)
    raised_date = models.DateTimeField(default=timezone.now)
    resolved_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'vendor_portal_issues'
        ordering = ['-raised_date']


class VendorReview(models.Model):
    DECISION_APPROVED = 'approved'
    DECISION_REJECTED = 'rejected'
    DECISION_REVISION = 'revision_requested'
    DECISION_VERIFIED = 'verified'
    DECISION_CHOICES = [
        (DECISION_APPROVED, 'Approved'),
        (DECISION_REJECTED, 'Rejected'),
        (DECISION_REVISION, 'Revision Requested'),
        (DECISION_VERIFIED, 'Verified'),
    ]

    daily_update = models.ForeignKey(VendorDailyUpdate, on_delete=models.CASCADE, related_name='reviews')
    reviewer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='vendor_portal_reviews')
    decision = models.CharField(max_length=30, choices=DECISION_CHOICES)
    comments = models.TextField(blank=True)
    reviewed_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'vendor_portal_reviews'
        ordering = ['-reviewed_at']


class VendorNotification(models.Model):
    CHANNEL_ERP = 'erp'
    CHANNEL_EMAIL = 'email'
    CHANNEL_WHATSAPP = 'whatsapp'
    CHANNEL_CHOICES = [
        (CHANNEL_ERP, 'ERP Notification'),
        (CHANNEL_EMAIL, 'Email'),
        (CHANNEL_WHATSAPP, 'WhatsApp'),
    ]
    STATUS_PENDING = 'pending'
    STATUS_SENT = 'sent'
    STATUS_READ = 'read'
    STATUS_FAILED = 'failed'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_SENT, 'Sent'),
        (STATUS_READ, 'Read'),
        (STATUS_FAILED, 'Failed'),
    ]

    recipient = models.ForeignKey(VendorUser, on_delete=models.CASCADE, related_name='notifications')
    assignment = models.ForeignKey(VendorProjectAssignment, on_delete=models.CASCADE, related_name='notifications', null=True, blank=True)
    daily_update = models.ForeignKey(VendorDailyUpdate, on_delete=models.CASCADE, related_name='notifications', null=True, blank=True)
    issue = models.ForeignKey(VendorIssue, on_delete=models.CASCADE, related_name='notifications', null=True, blank=True)
    title = models.CharField(max_length=255)
    message = models.TextField()
    channel = models.CharField(max_length=20, choices=CHANNEL_CHOICES, default=CHANNEL_ERP)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    created_at = models.DateTimeField(default=timezone.now)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'vendor_portal_notifications'
        ordering = ['-created_at']


class VendorPortalSession(models.Model):
    vendor_user = models.ForeignKey(VendorUser, on_delete=models.CASCADE, related_name='portal_sessions')
    session_key = models.CharField(max_length=80, blank=True)
    ip_address = models.CharField(max_length=100, blank=True)
    user_agent = models.TextField(blank=True)
    logged_in_at = models.DateTimeField(default=timezone.now)
    last_activity_at = models.DateTimeField(default=timezone.now)
    logged_out_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'vendor_portal_sessions'
        ordering = ['-last_activity_at']
