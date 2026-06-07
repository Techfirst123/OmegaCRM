from django.conf import settings
from django.db import models
from django.utils import timezone

from permissions.constants import ROLE_CHOICES


class SingletonStampedModel(models.Model):
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='%(class)s_updated',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class CompanySetting(SingletonStampedModel):
    company_name = models.CharField(max_length=255, default='Omega Group')
    company_logo = models.FileField(upload_to='company_settings/logos/', blank=True, null=True)
    company_address = models.TextField(blank=True)
    gst_number = models.CharField(max_length=50, blank=True)
    pan_number = models.CharField(max_length=50, blank=True)
    cin_number = models.CharField(max_length=50, blank=True)
    company_email = models.EmailField(blank=True)
    company_phone = models.CharField(max_length=50, blank=True)
    website_url = models.URLField(blank=True)
    bank_details = models.TextField(blank=True)
    authorized_signatory = models.CharField(max_length=255, blank=True)
    digital_signature = models.FileField(upload_to='company_settings/signatures/', blank=True, null=True)
    company_seal = models.FileField(upload_to='company_settings/seals/', blank=True, null=True)

    class Meta:
        db_table = 'company_settings'

    def __str__(self):
        return self.company_name


class ERPConfiguration(SingletonStampedModel):
    financial_year = models.CharField(max_length=30, blank=True, default='2026-2027')
    default_currency = models.CharField(max_length=20, blank=True, default='INR')
    tax_settings_json = models.TextField(blank=True, default='{}')
    gst_settings_json = models.TextField(blank=True, default='{}')
    invoice_number_format = models.CharField(max_length=120, blank=True, default='OMEGA/INV/{YEAR}/{AUTO_ID}')
    po_number_format = models.CharField(max_length=120, blank=True, default='OMEGA/PO/{YEAR}/{AUTO_ID}')
    vendor_code_format = models.CharField(max_length=120, blank=True, default='VEN-{AUTO_ID}')
    employee_code_format = models.CharField(max_length=120, blank=True, default='EMP-{AUTO_ID}')
    project_code_format = models.CharField(max_length=120, blank=True, default='PRJ-{YEAR}-{AUTO_ID}')

    class Meta:
        db_table = 'erp_configurations'

    def __str__(self):
        return 'ERP Configuration'


class SecuritySetting(SingletonStampedModel):
    minimum_password_length = models.PositiveIntegerField(default=8)
    require_uppercase = models.BooleanField(default=True)
    require_numbers = models.BooleanField(default=True)
    require_special_characters = models.BooleanField(default=False)
    session_timeout_minutes = models.PositiveIntegerField(default=60)
    ip_restrictions = models.TextField(blank=True)
    device_restrictions = models.TextField(blank=True)
    login_attempt_limit = models.PositiveIntegerField(default=5)
    audit_logging_enabled = models.BooleanField(default=True)
    force_password_change_days = models.PositiveIntegerField(default=90)
    two_factor_required = models.BooleanField(default=False)

    class Meta:
        db_table = 'security_settings'

    def __str__(self):
        return 'Security Settings'


class EmailConfiguration(SingletonStampedModel):
    smtp_host = models.CharField(max_length=255, blank=True)
    smtp_port = models.PositiveIntegerField(default=587)
    smtp_username = models.CharField(max_length=255, blank=True)
    smtp_password = models.CharField(max_length=255, blank=True)
    sender_email = models.EmailField(blank=True)
    sender_name = models.CharField(max_length=255, blank=True)
    email_template_header = models.TextField(blank=True)
    email_template_footer = models.TextField(blank=True)

    class Meta:
        db_table = 'email_configurations'

    def __str__(self):
        return 'Email Configuration'


class WhatsAppConfiguration(SingletonStampedModel):
    api_provider = models.CharField(max_length=120, blank=True)
    access_token = models.TextField(blank=True)
    phone_number_id = models.CharField(max_length=120, blank=True)
    business_account_id = models.CharField(max_length=120, blank=True)
    webhook_url = models.URLField(blank=True)
    template_management_json = models.TextField(blank=True, default='{}')

    class Meta:
        db_table = 'whatsapp_configurations'

    def __str__(self):
        return 'WhatsApp Configuration'


class AppearanceSetting(SingletonStampedModel):
    erp_logo = models.FileField(upload_to='appearance/logos/', blank=True, null=True)
    sidebar_logo = models.FileField(upload_to='appearance/sidebar/', blank=True, null=True)
    login_page_banner = models.FileField(upload_to='appearance/banners/', blank=True, null=True)
    favicon = models.FileField(upload_to='appearance/favicon/', blank=True, null=True)
    brand_primary_color = models.CharField(max_length=20, blank=True, default='#0d5cab')
    brand_secondary_color = models.CharField(max_length=20, blank=True, default='#1b7f7a')
    custom_css = models.TextField(blank=True)

    class Meta:
        db_table = 'appearance_settings'

    def __str__(self):
        return 'Appearance Settings'


class DashboardSetting(SingletonStampedModel):
    widget_configuration_json = models.TextField(blank=True, default='{}')
    hidden_modules_json = models.TextField(blank=True, default='[]')
    quick_links_json = models.TextField(blank=True, default='[]')
    custom_dashboard_json = models.TextField(blank=True, default='{}')

    class Meta:
        db_table = 'dashboard_settings'

    def __str__(self):
        return 'Dashboard Settings'


class MasterDataEntry(models.Model):
    TYPE_VENDOR_CATEGORY = 'vendor_category'
    TYPE_MATERIAL_CATEGORY = 'material_category'
    TYPE_PROJECT_TYPE = 'project_type'
    TYPE_DEPARTMENT = 'department'
    TYPE_DESIGNATION = 'designation'
    TYPE_LOCATION = 'location'
    TYPE_TAX_CATEGORY = 'tax_category'
    TYPE_PAYMENT_MODE = 'payment_mode'
    TYPE_CHOICES = [
        (TYPE_VENDOR_CATEGORY, 'Vendor Categories'),
        (TYPE_MATERIAL_CATEGORY, 'Material Categories'),
        (TYPE_PROJECT_TYPE, 'Project Types'),
        (TYPE_DEPARTMENT, 'Departments'),
        (TYPE_DESIGNATION, 'Designations'),
        (TYPE_LOCATION, 'Locations'),
        (TYPE_TAX_CATEGORY, 'Tax Categories'),
        (TYPE_PAYMENT_MODE, 'Payment Modes'),
    ]

    master_type = models.CharField(max_length=40, choices=TYPE_CHOICES)
    name = models.CharField(max_length=150)
    code = models.CharField(max_length=80, blank=True)
    display_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    metadata_json = models.TextField(blank=True, default='{}')

    class Meta:
        db_table = 'master_data_entries'
        unique_together = ('master_type', 'name')
        ordering = ['master_type', 'display_order', 'name']

    def __str__(self):
        return f'{self.get_master_type_display()} - {self.name}'


class UserNotificationPreference(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notification_settings')
    email_notifications = models.BooleanField(default=True)
    sms_notifications = models.BooleanField(default=False)
    whatsapp_notifications = models.BooleanField(default=False)
    in_app_notifications = models.BooleanField(default=True)
    browser_push_notifications = models.BooleanField(default=False)
    event_preferences_json = models.TextField(blank=True, default='{}')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'user_notification_preferences'

    def __str__(self):
        return f'Notification Preferences - {self.user}'


class SystemAuditLog(models.Model):
    ACTION_LOGIN = 'login'
    ACTION_LOGOUT = 'logout'
    ACTION_PASSWORD_CHANGE = 'password_change'
    ACTION_USER_CREATE = 'user_create'
    ACTION_USER_DELETE = 'user_delete'
    ACTION_VENDOR_ASSIGNMENT = 'vendor_assignment'
    ACTION_PO_CHANGE = 'po_change'
    ACTION_PAYMENT_UPDATE = 'payment_update'
    ACTION_SETTINGS_CHANGE = 'settings_change'
    ACTION_GENERIC = 'generic'
    ACTION_CHOICES = [
        (ACTION_LOGIN, 'Login'),
        (ACTION_LOGOUT, 'Logout'),
        (ACTION_PASSWORD_CHANGE, 'Password Change'),
        (ACTION_USER_CREATE, 'User Creation'),
        (ACTION_USER_DELETE, 'User Deletion'),
        (ACTION_VENDOR_ASSIGNMENT, 'Vendor Assignment'),
        (ACTION_PO_CHANGE, 'PO Change'),
        (ACTION_PAYMENT_UPDATE, 'Payment Update'),
        (ACTION_SETTINGS_CHANGE, 'Settings Change'),
        (ACTION_GENERIC, 'Generic'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='system_audit_logs')
    action = models.CharField(max_length=40, choices=ACTION_CHOICES, default=ACTION_GENERIC)
    module = models.CharField(max_length=80)
    description = models.TextField(blank=True)
    ip_address = models.CharField(max_length=100, blank=True)
    device_information = models.TextField(blank=True)
    metadata_json = models.TextField(blank=True, default='{}')
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'system_audit_logs'
        ordering = ['-created_at', '-id']

    def __str__(self):
        return f'{self.module} - {self.action}'


class UserSessionRecord(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='session_records')
    session_key = models.CharField(max_length=80, blank=True)
    ip_address = models.CharField(max_length=100, blank=True)
    user_agent = models.TextField(blank=True)
    logged_in_at = models.DateTimeField(default=timezone.now)
    last_activity_at = models.DateTimeField(default=timezone.now)
    logged_out_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'user_session_records'
        ordering = ['-last_activity_at', '-logged_in_at']

    def __str__(self):
        return f'{self.user} - {self.session_key}'


class LoginAttempt(models.Model):
    username = models.CharField(max_length=150)
    ip_address = models.CharField(max_length=100, blank=True)
    success = models.BooleanField(default=False)
    attempted_at = models.DateTimeField(default=timezone.now)
    detail = models.TextField(blank=True)

    class Meta:
        db_table = 'login_attempts'
        ordering = ['-attempted_at']


class BackupRecord(models.Model):
    TYPE_MANUAL = 'manual'
    TYPE_SCHEDULED = 'scheduled'
    TYPE_CHOICES = [
        (TYPE_MANUAL, 'Manual'),
        (TYPE_SCHEDULED, 'Scheduled'),
    ]

    backup_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default=TYPE_MANUAL)
    file = models.FileField(upload_to='system_backups/', blank=True, null=True)
    note = models.CharField(max_length=255, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='backup_records')
    created_at = models.DateTimeField(default=timezone.now)
    restored_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'backup_records'
        ordering = ['-created_at']


class SupportTicket(models.Model):
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

    title = models.CharField(max_length=255)
    description = models.TextField()
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='support_tickets')
    assigned_role = models.CharField(max_length=40, choices=ROLE_CHOICES, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_OPEN)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'support_tickets'
        ordering = ['-updated_at', '-created_at']

    def __str__(self):
        return self.title


class HelpResource(models.Model):
    TYPE_DOC = 'documentation'
    TYPE_VIDEO = 'video'
    TYPE_FAQ = 'faq'
    TYPE_CHOICES = [
        (TYPE_DOC, 'Documentation'),
        (TYPE_VIDEO, 'Video Tutorial'),
        (TYPE_FAQ, 'FAQ'),
    ]

    resource_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    title = models.CharField(max_length=255)
    url = models.URLField(blank=True)
    content = models.TextField(blank=True)
    is_published = models.BooleanField(default=True)
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'help_resources'
        ordering = ['resource_type', 'display_order', 'title']

    def __str__(self):
        return self.title
